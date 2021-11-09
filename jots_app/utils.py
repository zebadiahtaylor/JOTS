from django.core.files.storage import default_storage

from markdown2 import Markdown

from .models import Collection, Note, Tag, Article

""" users """

def user_has_follower_permissions(collection_id, user):
    """
    Checks if user is both a follower or a leader of a collection. 
    For leader only, reference collection_object.leader
    """
    collection = Collection.objects.get(id=collection_id)
    if user.is_authenticated:
        if collection.leader == user or collection.followers.filter(id=user.id).exists():
            return True
    return False


def return_rows_for_editing_content(content):
    rows = 2
    for x in content:
        if x == '/':
            rows += 1
    if rows < 6:
        rows = 6
    if rows >20:
        rows = 20
    return rows

""" collections data"""

def get_collection_page_data(collection):
    collection = Collection.objects.get(id=collection)
    notes = Note.objects.filter(collection=collection).order_by('-created_at')[:10]
    tags = Tag.objects.filter(collection=collection).order_by('name')
    articles = Article.objects.filter(collection=collection).order_by('-views')[:15]
    return collection, notes, tags, articles


def get_leaders_collections(user):
    collections = Collection.objects.filter(leader=user)
    return collections


def get_followers_collections(user):
    collections = Collection.objects.filter(followers=user)
    return collections


def get_users_collections(user):
    leader_collections = get_leaders_collections(user)
    follower_collections = get_followers_collections(user)
    return leader_collections, follower_collections



""" articles and markdown """


def render_markdowned(slug):
    """
    Converts md files into html. 
    Use {{ variable|safe }} in html files 
    """
    markdowner = Markdown()
    return markdowner.convert(get_article(slug))

def render_terms(slug):
    markdowner = Markdown()
    file = default_storage.open(f"{slug}.md")
    content = file.read().decode("utf-8")
    return markdowner.convert(content)

def get_article(slug):
    # try:
    file = default_storage.open(f"articles/{slug}.md")
    return file.read().decode("utf-8")


""" variables """

planned_upcoming_features = ['Improved Auto-Sorting',
                            'Improved Searching', 
                            'Improved Formatting and Readability',
                            'User-created and auto-generated quizzes',
                            'Status Rewards for note-taking',
                            ]