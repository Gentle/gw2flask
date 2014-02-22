from gevent import monkey
monkey.patch_all()

import gevent
from gevent.queue import JoinableQueue

from gw2api import api
import redistypes
#from redistypes import RedisHashSet

items = redistypes.RedisHashSet(('gw2', 'items'))
recipes = redistypes.RedisHashSet(('gw2', 'recipes'))

queue = JoinableQueue()

num_worker_threads = 100


def import_item(item_id, force=False):
    if not item_id in items:
        item = api.get_item(item_id)
        if item:
            print item.get('name')
            items[item_id] = item


def import_recipe(recipe_id, force=False):
    if not recipe_id in recipes:
        recipe = api.get_recipe(recipe_id)
        if recipe:
            print recipe.get('recipe_id')
            recipes[recipe_id] = recipe


def worker():
    while True:
        (id, import_fn) = queue.get()
        try:
            import_fn(id)
        finally:
            queue.task_done()


def import_all():
    for i in range(num_worker_threads):
        gevent.spawn(worker)
    ## items
    ids = api.get_items()
    print len(items), "/", len(ids), "items"
    for item_id in ids:
        queue.put((item_id, import_item))
    ## recipes
    ids = api.get_recipes()
    print len(recipes), "/", len(ids), "recipes"
    for recipe_id in ids:
        queue.put((recipe_id, import_recipe))
    # wait for jobs to finish
    queue.join()


def items_with_recipes():
    for key in recipes:
        item_id = recipes[key].get('output_item_id')
        item = items.get(item_id)
        if item:
            name = item.get('name')
            if 'volcanus' in name.lower():
                print name

if __name__ == '__main__':
    import_all()
    #items_with_recipes()
