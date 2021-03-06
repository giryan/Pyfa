#===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eos.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from eos.db import gamedata_session
from eos.db.gamedata.metaGroup import metatypes_table, items_table
from sqlalchemy.sql import and_, or_, select, func
from sqlalchemy.orm import join, exc
from eos.types import Item, Category, Group, MarketGroup, AttributeInfo, MetaData, MetaGroup
from eos.db.util import processEager, processWhere
import eos.config

configVal = getattr(eos.config, "gamedataCache", None)
if configVal is True:
    def cachedQuery(amount, *keywords):
        def deco(function):
            cache = {}
            def checkAndReturn(*args, **kwargs):
                useCache = kwargs.pop("useCache", True)
                cacheKey = []
                cacheKey.extend(args)
                for keyword in keywords:
                    cacheKey.append(kwargs.get(keyword))

                cacheKey = tuple(cacheKey)
                handler = cache.get(cacheKey)
                if handler is None or not useCache:
                    handler = cache[cacheKey] = function(*args, **kwargs)

                return handler

            return checkAndReturn
        return deco

elif callable(configVal):
    cachedQuery = eos.config.gamedataCache
else:
    def cachedQuery(amount, *keywords):
        def deco(function):
            def checkAndReturn(*args, **kwargs):
                return function(*args, **kwargs)

            return checkAndReturn
        return deco

def sqlizeString(line):
    # Escape backslashes first, as they will be as escape symbol in queries
    # Then escape percent and underscore signs
    # Finally, replace generic wildcards with sql-style wildcards
    line = line.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("*", "%")
    return line

itemNameMap = {}
@cachedQuery(1, "lookfor")
def getItem(lookfor, eager=None):
    if isinstance(lookfor, int):
        if eager is None:
            item = gamedata_session.query(Item).get(lookfor)
        else:
            item = gamedata_session.query(Item).options(*processEager(eager)).filter(Item.ID == lookfor).first()
    elif isinstance(lookfor, basestring):
        if lookfor in itemNameMap:
            id = itemNameMap[lookfor]
            if eager is None:
                item = gamedata_session.query(Item).get(id)
            else:
                item = gamedata_session.query(Item).options(*processEager(eager)).filter(Item.ID == id).first()
        else:
            # Item names are unique, so we can use first() instead of one()
            item = gamedata_session.query(Item).options(*processEager(eager)).filter(Item.name == lookfor).first()
            itemNameMap[lookfor] = item.ID
    else:
        raise TypeError("Need integer or string as argument")
    return item

groupNameMap = {}
@cachedQuery(1, "lookfor")
def getGroup(lookfor, eager=None):
    if isinstance(lookfor, int):
        if eager is None:
            group = gamedata_session.query(Group).get(lookfor)
        else:
            group = gamedata_session.query(Group).options(*processEager(eager)).filter(Group.ID == lookfor).first()
    elif isinstance(lookfor, basestring):
        if lookfor in groupNameMap:
            id = groupNameMap[lookfor]
            if eager is None:
                group = gamedata_session.query(Group).get(id)
            else:
                group = gamedata_session.query(Group).options(*processEager(eager)).filter(Group.ID == id).first()
        else:
            # Group names are unique, so we can use first() instead of one()
            group = gamedata_session.query(Group).options(*processEager(eager)).filter(Group.name == lookfor).first()
            groupNameMap[lookfor] = group.ID
    else:
        raise TypeError("Need integer or string as argument")
    return group

categoryNameMap = {}
@cachedQuery(1, "lookfor")
def getCategory(lookfor, eager=None):
    if isinstance(lookfor, int):
        if eager is None:
            category = gamedata_session.query(Category).get(lookfor)
        else:
            category = gamedata_session.query(Category).options(*processEager(eager)).filter(Category.ID == lookfor).first()
    elif isinstance(lookfor, basestring):
        if lookfor in categoryNameMap:
            id = categoryNameMap[lookfor]
            if eager is None:
                category = gamedata_session.query(Category).get(id)
            else:
                category = gamedata_session.query(Category).options(*processEager(eager)).filter(Category.ID == id).first()
        else:
            # Category names are unique, so we can use first() instead of one()
            category = gamedata_session.query(Category).options(*processEager(eager)).filter(Category.name == lookfor).first()
            categoryNameMap[lookfor] = category.ID
    else:
        raise TypeError("Need integer or string as argument")
    return category

metaGroupNameMap = {}
@cachedQuery(1, "lookfor")
def getMetaGroup(lookfor, eager=None):
    if isinstance(lookfor, int):
        if eager is None:
            metaGroup = gamedata_session.query(MetaGroup).get(lookfor)
        else:
            metaGroup = gamedata_session.query(MetaGroup).options(*processEager(eager)).filter(MetaGroup.ID == lookfor).first()
    elif isinstance(lookfor, basestring):
        if lookfor in metaGroupNameMap:
            id = metaGroupNameMap[lookfor]
            if eager is None:
                metaGroup = gamedata_session.query(MetaGroup).get(id)
            else:
                metaGroup = gamedata_session.query(MetaGroup).options(*processEager(eager)).filter(MetaGroup.ID == id).first()
        else:
            # MetaGroup names are unique, so we can use first() instead of one()
            metaGroup = gamedata_session.query(MetaGroup).options(*processEager(eager)).filter(MetaGroup.name == lookfor).first()
            metaGroupNameMap[lookfor] = metaGroup.ID
    else:
        raise TypeError("Need integer or string as argument")
    return metaGroup

@cachedQuery(1, "lookfor")
def getMarketGroup(lookfor, eager=None):
    if isinstance(lookfor, int):
        if eager is None:
            marketGroup = gamedata_session.query(MarketGroup).get(lookfor)
        else:
            marketGroup = gamedata_session.query(MarketGroup).options(*processEager(eager)).filter(MarketGroup.ID == lookfor).first()
    else:
        raise TypeError("Need integer as argument")
    return marketGroup

@cachedQuery(2, "where", "filter")
def getItemsByCategory(filter, where=None, eager=None):
    if isinstance(filter, int):
        filter = Category.ID == filter
    elif isinstance(filter, basestring):
        filter = Category.name == filter
    else:
        raise TypeError("Need integer or string as argument")

    filter = processWhere(filter, where)
    return gamedata_session.query(Item).options(*processEager(eager)).join(Item.group, Group.category).filter(filter).all()

@cachedQuery(3, "where", "nameLike", "join")
def searchItems(nameLike, where=None, join=None, eager=None):
    if not isinstance(nameLike, basestring):
        raise TypeError("Need string as argument")

    if join is None:
        join = tuple()

    if not hasattr(join, "__iter__"):
        join = (join,)

    items = gamedata_session.query(Item).options(*processEager(eager)).join(*join)
    for token in nameLike.split(' '):
        token_safe = u"%{0}%".format(sqlizeString(token))
        items = items.filter(and_(Item.name.like(token_safe, escape="\\"), where))
    items = items.limit(100).all()
    return items

@cachedQuery(2, "where", "itemids")
def getVariations(itemids, where=None, eager=None):
    for itemid in itemids:
        if not isinstance(itemid, int):
            raise TypeError("All passed item IDs must be integers")
    # Get out if list of provided IDs is empty
    if len(itemids) == 0:
        return []

    itemfilter = or_(*(metatypes_table.c.parentTypeID == itemid for itemid in itemids))
    filter = processWhere(itemfilter, where)
    joinon = items_table.c.typeID == metatypes_table.c.typeID
    vars = gamedata_session.query(Item).options(*processEager(eager)).join((metatypes_table, joinon)).filter(filter).all()
    return vars

@cachedQuery(1, "attr")
def getAttributeInfo(attr, eager=None):
    if isinstance(attr, basestring):
        filter = AttributeInfo.name == attr
    elif isinstance(attr, int):
        filter = AttributeInfo.ID == attr
    else:
        raise TypeError("Need integer or string as argument")
    try:
        result = gamedata_session.query(AttributeInfo).options(*processEager(eager)).filter(filter).one()
    except exc.NoResultFound:
        result = None
    return result

@cachedQuery(1, "field")
def getMetaData(field):
    if isinstance(field, basestring):
        data = gamedata_session.query(MetaData).get(field)
    else:
        raise TypeError("Need string as argument")
    return data

@cachedQuery(2, "itemIDs", "attributeID")
def directAttributeRequest(itemIDs, attrIDs):
    for itemID in itemIDs:
        if not isinstance(itemID, int):
            raise TypeError("All attrIDs must be integer")
    for itemID in itemIDs:
        if not isinstance(itemID, int):
            raise TypeError("All itemIDs must be integer")

    q = select((eos.types.Item.typeID, eos.types.Attribute.attributeID, eos.types.Attribute.value),
                                  and_(eos.types.Attribute.attributeID.in_(attrIDs), eos.types.Item.typeID.in_(itemIDs)),
                                  from_obj=[join(eos.types.Attribute, eos.types.Item)])

    result = gamedata_session.execute(q).fetchall()
    return result
