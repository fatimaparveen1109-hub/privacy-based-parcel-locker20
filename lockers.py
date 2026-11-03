from db import query
def hubs(): return query("SELECT id,name,city FROM hubs WHERE is_active=TRUE ORDER BY name")
