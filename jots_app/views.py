from django import forms
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db import IntegrityError
from django.urls import reverse

from .forms import *
from .models import User, Collection, Note, Tag, Article
from . import utils

# Create your views here.

def test(request):
    return render(request, "jots/test.html")


def index(request):
    """
    Gateway to various editions / groups / articles / notes.
    Should be highly adjustable based on user usage.
    """
    if request.user.is_authenticated:
        leader_collections, follower_collections = utils.get_users_collections(request.user)

        user = User.objects.get(id=request.user.id)
        return render(request, "jots/collections.html", {
            'leader_collections': leader_collections,
            'follower_collections': follower_collections, 
            'invites': [x for x in user.collection_invites.all()],
            'inviteform': AcceptGroupInviteForm(),
            })
    else:
        return HttpResponseRedirect(reverse("landing"))

def landing(request):
    return render(request, 'jots/landing.html')

def error(request, code=404):
    # TODO
    return render(request, "jots/error.html", {
        "code": code,
    })


"""collections"""

def collections(request):
    if request.user.is_authenticated:
        leader_collections, follower_collections = utils.get_users_collections(request.user)
        
        user = User.objects.get(id=request.user.id) 

        return render(request, "jots/collections.html", {
            'leader_collections': leader_collections,
            'follower_collections': follower_collections, 
            'invites': [x for x in user.collection_invites.all()],
            'inviteform': AcceptGroupInviteForm(),
            })
    else:
        return HttpResponseRedirect(reverse("landing"))


def collection_main(request, collection_id):
    """Shows Recent Notes, and most popular article titles of a given collection"""
    is_member = utils.user_has_follower_permissions(collection_id, request.user)
    collection = Collection.objects.get(id=collection_id)

    if is_member or collection.is_public:
        collection, notes, tags, articles = utils.get_collection_page_data(collection_id)

        class NewNoteForm(NoteForm):
            #TODO hide these monsters in static methods in forms.py
            tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Select a tag", label="")

        return render(request, "jots/collection_main.html", {
            'collection': collection,
            'notes': notes,
            'tags': tags,
            'articles': articles,
            'is_member': is_member,
            'noteform': NewNoteForm(),
            })

    else:
        return HttpResponseRedirect(reverse("index"))


def collection_manage(request, collection_id):
    collection = Collection.objects.get(id=collection_id)

    if request.user.is_authenticated and request.user == collection.leader:
        form = InviteToJotsForm()
        invitetogroupform = InviteToGroupForm()
        return render(request, "jots/collection_manage.html", {
            'collection': collection,
            'form': form,
            'invitetogroupform' : invitetogroupform,
            'followers': [p for p in collection.followers.all().order_by('username')],
        })

    else:
        return HttpResponseRedirect(reverse("landing"))
    

def collection_create(request):
    if request.user.is_authenticated:

        if request.method == "POST":
            collection = CollectionForm.create_collection(request.user, 
                                            form=CollectionForm(request.POST)
                                            )
            return redirect(reverse("collection_manage", 
                                    kwargs={"collection_id": collection.id}))

        else:
            form = CollectionForm()
            return render(request, "jots/collection_create.html", {
            "form": form,
            })

    else:
        return HttpResponseRedirect(reverse("landing"))


def collection_edit(request, collection_id): 
    collection = Collection.objects.get(id=collection_id)

    if request.user.is_authenticated and request.user == collection.leader:

        if request.method == "POST":
            form = CollectionForm(request.POST)
            collection = CollectionForm.edit_collection(request.user, form, collection)

            if collection:
            
                return redirect(reverse("collection", kwargs={"collection_id": collection.id}))

        else:
            form = CollectionForm.populate_edit_collection_form(collection_id)

            return render(request, "jots/collection_edit.html", {
                'collection': collection,
                'form': form
                })

    return HttpResponseRedirect(reverse("landing"))


def collection_delete(request, collection_id):
    collection = Collection.objects.get(id=collection_id)

    if request.user.is_authenticated and request.user == collection.leader: 
        if request.method == "POST":
            message = DeleteCollectionForm.delete_collection(collection_id, 
                            request.POST)

            return render(request, "jots/collections.html", {
                'message': message,
                'leader_collections': utils.get_leaders_collections(request.user),
                'follower_collections': utils.get_followers_collections(request.user), 
                })

        else:
            form = DeleteCollectionForm()

            return render(request, "jots/collection_delete.html", {
                "collection": collection,
                "form": form,
                })

    else:
        return HttpResponseRedirect(reverse("landing"))


def collection_find(request):
    """
    Allows user to browse for publicly available collections.
    """
    return render(request, "jots/collection_find.html", {
        "collections": Collection.objects.filter(is_public=True).order_by('title')
        })


def collection_request(request, collection_id): 
    """
    DISABLED
    """
    if request.user.is_authenticated:
        collection = Collection.objects.get(id=collection_id)
        if request.method == "POST" and collection.is_public:
            pass

        else:
            form = RequestForm()
            return render(request, "jots/collection_request.html", {
                "collection": collection,
                "form": form,
                })
        return redirect(reverse("landing"))

    else:
        return redirect(reverse("login"))


def collection_complete(request, collection_id):
    """
    TODO
    """
    collection = Collection.objects.get(id=collection_id)

    if request.user.is_authenticated and request.user == collection.leader: 
        leader_collections, follower_collections = utils.get_users_collections(request.user)
        return render(request, "jots/collections.html", {
                'message': "This feature isn't available yet.",
                'leader_collections': leader_collections,
                'follower_collections': follower_collections, 
                })
    else:
        return HttpResponseRedirect(reverse("landing"))


""" NOTES AND ARTICLES """


def notes(request, collection_id):
    """
    Primary Notes Page. Write Notes / Read & Edit Recents.
    """
    collection = Collection.objects.get(id=collection_id)
    notes = Note.objects.filter(collection=collection_id)
    tags = Tag.objects.filter(collection=collection_id)
    is_member = utils.user_has_follower_permissions(collection_id, request.user)

    last_tag = None # for auto-selecting most recent tag.

    if request.method == "POST":
        if "note" in request.POST and is_member:
            form = NoteForm(request.POST)
            if form.is_valid():

                # tag = TagForm.process_tag(form, collection.id)

                note = form.create_and_return_note(collection,
                                        form,
                                        request.user)
                
                if note.tag != None:
                    last_tag = Tag.objects.get(name=note.tag, collection=collection)


        elif request.POST['filter_by_tag'] != "":
            # and isinstance(request.POST['filter_by_text'], str) and len(request.POST['filter_by_text']) > 0
            notes = Note.objects.filter(collection=collection_id).filter(tag__name__contains=(request.POST['filter_by_tag']))

        elif request.POST['filter_by_text'] != "":
            print(f"{request.POST['filter_by_text']}")
            notes = Note.objects.filter(collection=collection_id).filter(text__contains=request.POST['filter_by_text'])
        

    if collection.is_public or is_member:

        if last_tag == None:
            class NewNoteForm(NoteForm):
                #TODO hide these monsters in static methods in forms.py
                tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Select a tag", label="")

        else:
            class NewNoteForm(NoteForm):
                #TODO hide these monsters in static methods in forms.py
                tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Select a tag", initial=last_tag, label="")

        class EditNoteForm(NoteForm):
            tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Select tag to retag", label="")



        return render(request, "jots/notes.html", {
            'collection': collection,
            'notes': notes.order_by("-created_at")[:40],
            'tags': tags.order_by("name"),
            'noteform': NewNoteForm(),
            'is_member': is_member,
            'editnoteform': EditNoteForm(auto_id='id_for_%s')
            })

def notes_all(request, collection_id):
    """
    TODO: Add organize notes by date (group by day etc.).
    TODO: handle note-organization requests. Eliminate repetition. 
    """
    collection = Collection.objects.get(id=collection_id)
    notes = Note.objects.filter(collection=collection_id).order_by("-created_at")
    tags = Tag.objects.filter(collection=collection_id)
    is_member = utils.user_has_follower_permissions(collection_id, request.user)


    if is_member or collection.is_public:
        class EditNoteForm(NoteForm):
            tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Select tag to retag", label="")

        return render(request, "jots/notes_all.html", {
            'collection': collection,
            'notes': notes.order_by("-created_at"),
            'tags': tags.order_by("name"),
            'editnoteform': EditNoteForm(auto_id='id_for_%s'),
            'is_member': is_member,
            })

    else:
        return HttpResponseRedirect(reverse("landing"))


def note_edit(request, note_id):

    note = Note.objects.get(pk=note_id)

    if request.method == "POST" and utils.user_has_follower_permissions(note.collection.id, request.user):
            form = NoteForm(request.POST)
            if form.is_valid():
                form.save_note_edit(note, form, request.user)
                return redirect(reverse("notes", args=(note.collection.id,)))

    else:
        return HttpResponseRedirect(reverse("landing"))

def note_delete(request, note_id):
    note = Note.objects.get(pk=note_id)

    if request.method == "POST" and utils.user_has_follower_permissions(note.collection.id, request.user):
        note.delete()
        return redirect(reverse("notes", args=(note.collection.id,)))
        
    else:
        return HttpResponseRedirect(reverse("landing"))

def article(request, article_id):
    article = Article.objects.get(id=article_id)
    is_member = utils.user_has_follower_permissions(article.collection.id, request.user)


    class EditNoteForm(NoteForm):
        tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=article.collection.id), required=False, empty_label="Select tag to retag", label="")
    
    if is_member or article.collection.is_public:
        article.views += 1
        article.save()
        return render(request, "jots/article.html", {
            'article': article,
            'content': utils.render_markdowned(article.content_slug),
            'collection': Collection.objects.get(id=article.collection.id),
            'notes': Note.objects.filter(collection=article.collection).filter(tag=article.tag),
            'is_member': is_member,
            'editnoteform': EditNoteForm(auto_id='id_for_%s')
            })

    else:
        return HttpResponseRedirect(reverse("landing"))

def articles(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    is_member = utils.user_has_follower_permissions(collection_id, request.user)
    
    if is_member or collection.is_public:
        articles = Article.objects.filter(collection=collection_id)

        return render(request, "jots/articles.html", {
            'collection': collection,
            'top_articles': articles.order_by("views"),
            'articles': articles.order_by('title'),
            'is_member': is_member,
            })

    else:
        return HttpResponseRedirect(reverse("landing"))

def articles_all(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    is_member = utils.user_has_follower_permissions(collection_id, request.user)

    if is_member or collection.is_public:
        articles = Article.objects.filter(collection=collection_id)

        return render(request, "jots/articles_all.html", {
            'collection': collection,
            'articles': articles.order_by('title'),
            'is_member': is_member,
            })

def article_create(request, collection_id):
    if utils.user_has_follower_permissions(collection_id, request.user):
        if request.method == "POST":
            new_article = ArticleForm.create_and_return_article(
                                            collection_id,
                                            request.user,
                                            form=ArticleForm(request.POST)
                                            )

            return redirect(reverse("article", kwargs={
                "article_id": new_article.id
                }))

        else:
            if utils.user_has_follower_permissions(collection_id, request.user):
                class NewArticleForm(ArticleForm):
                    tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=collection_id), required=False, empty_label="Choose existing tag.", label="")
                form = NewArticleForm()

                return render(request, "jots/article_create.html", {
                    'collection': Collection.objects.get(id=collection_id),
                    'form': form
                    }) 

    else:
        return HttpResponseRedirect(reverse("landing"))

def article_edit(request, article_id):
    article = Article.objects.get(id=article_id)
    is_member = utils.user_has_follower_permissions(article.collection.id, request.user)

    if request.method == "POST" and is_member:
        
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.edit_article(article, form, request.user)
            return redirect(reverse("article", kwargs={
                "article_id": article.id,
                }))


    elif is_member:
        class EditArticleForm(ArticleForm):
            title = forms.CharField(max_length=100, required=True, initial=article.title)
            tag = forms.ModelChoiceField(queryset=Tag.objects.filter(collection=article.collection.id), initial=article.tag, required=False, empty_label="change tag.", label="")

        with open(f"articles/{article.content_slug}.md", 'r') as f:
            content = f.read()

        return render(request, "jots/article_edit.html", {
                'collection': Collection.objects.get(id=article.collection.id),
                'content': content,
                'article': article,
                'form': EditArticleForm(),
                'is_member': is_member,
                'delete_form': DeleteArticleForm(),
                'rows': utils.return_rows_for_editing_content(content),
                }) 

    else:
        return HttpResponseRedirect(reverse("landing"))

def article_append_note(request, article_id, note_id):
    article = Article.objects.get(pk=article_id)

    if request.method == "POST" and utils.user_has_follower_permissions(article.collection.id, request.user):
        ArticleForm.append_note(article, note_id)

        return redirect(reverse("article", kwargs={
            "article_id": article.id
            }))
    else: 
        return HttpResponseRedirect(reverse("landing"))

    
def article_delete(request, article_id):
    article = Article.objects.get(pk=article_id)
    is_member = utils.user_has_follower_permissions(article.collection.id, request.user)

    if is_member and request.method == "POST":
        message = DeleteArticleForm.delete_article(article_id, request.POST)

        return redirect(reverse("articles", kwargs={
            "collection_id": article.collection.id
            }))

    else:
        return HttpResponseRedirect(reverse("landing"))


def tags(request, collection_id):
    if utils.user_has_follower_permissions(collection_id, request.user):

        collection = Collection.objects.get(id=collection_id)
        message = ""

        class NewEditTagForm(EditTagForm):
            old_tag = forms.ModelChoiceField(queryset=Tag.objects.filter(
                                            collection=collection_id).order_by("name"),
                                            required=True, 
                                            empty_label="Edit a tag.")
        
        class ADeleteTagForm(DeleteTagForm):
            tag = forms.ModelChoiceField(queryset=Tag.objects.filter(
                                            collection=collection_id).order_by("name"),
                                            required=True, 
                                            empty_label="Delete a tag.",
                                            label="")
     
        if request.method == "POST":
            if 'make' in request.POST:
                TagForm.process_new_tag(collection_id, TagForm(request.POST))



            elif 'edit' in request.POST:
                message = TagForm.save_tag_edit(collection_id, 
                                            form=NewEditTagForm(request.POST)
                                            )

            elif 'delete' in request.POST:
                message = TagForm.delete_tag(collection_id,
                                        form=ADeleteTagForm(request.POST)
                                        )

        
        maketagform = TagForm()
        edittagform = NewEditTagForm()
        deletetagform = ADeleteTagForm()


        return render(request, "jots/tags.html",{
            "collection": collection,
            "tags": Tag.objects.filter(collection=collection).order_by("name"),
            "maketagform": maketagform,
            "edittagform": edittagform,
            "message": message,
            "deletetagform": deletetagform
        })

    else:
        render(request, "jots/landing.html")


""" About, User Profiles, Membership """


def about(request):
    """
    currently there's no link to this page. 
    """
    feedbackform = FeedbackForm(auto_id='')
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            message = form.cleaned_data["message"]
            form.email_feedback(request.user, name, message)
        return render(request, "jots/about.html", {
            "feedbackform": feedbackform,
            "features": utils.planned_upcoming_features,
            "message": "Thank you for your feedback! I may follow up with more questions.",
        })
    else:
        return render(request, "jots/about.html", {
            "feedbackform": feedbackform,
            "features": utils.planned_upcoming_features,
            })

def guide(request):
    """
    #TODO
    Ideally, this should be unnecessary.
    """
    return render(request, "jots/guide.html")


def profile(request, user_id):
    """
    Disabled.
    """
    if request.user.is_authenticated:
        return redirect(reverse("landing"))
        # if request.method == 'POST' and request.user.id == user_id:
        #     form = ProfileForm(request.POST)

        #     if form.is_valid():
        #         form.create_or_edit_profile(request.user, form)
        #         message = "Your Profile has been saved!"

        #     return redirect(reverse('profile', kwargs={
        #             'user_id': user_id,
        #             'message': message,
        #             }))

        # elif request.user.id == user_id:
        #     form = ProfileForm()
        #     try:
        #         profile = Profile.objects.get(user=user_id)
        #     except Profile.DoesNotExist:
        #         profile = None

        #     return render(request, "jots/profile.html", {
        #         'profile': profile,
        #         'form': form,
        #     })
        # elif request.method == 'GET':
        #     return redirect(reverse('profile', kwargs={
        #             'user_id': request.user.id,
        #             }))

    else:
        return redirect(reverse("landing"))


def profile_edit(request, user_id):
    """
    Disabled.
    """
    return render(request, "jots/landing.html")


def invite(request, collection_id):
    """
    Works. However, work on superior/more fluid authentication after shipping.
    """
    collection = Collection.objects.get(pk=collection_id)

    if request.method == 'POST' and collection.leader == request.user:
        if "jots_invite" in request.POST:
            form = InviteToJotsForm(request.POST)
            try:
                if form.is_valid():
                    email = form.cleaned_data["email"]
                    form.email_invite_to_jots(request.user, collection.title, email)
            except UnboundLocalError:
                # TODO Currently doesn't validate more than 1 email.
                print("oh fuck")
                pass
        elif "group_invite" in request.POST:
            form = InviteToGroupForm(request.POST)
            if form.is_valid():
                x = form.handle_invite(collection, form.cleaned_data["user"])


    return redirect(reverse("collection_manage", kwargs={
            "collection_id": collection_id,
            }))


def respond_to_invite(request, collection_id):
    if request.method == 'POST' and request.user.is_authenticated:
        message = ""
        form = AcceptGroupInviteForm(request.POST)
        if form.is_valid():
            if "1" in request.POST['response']:
                form.accept_invite(request.user, collection_id)
                message = "You have accepted the invite."
                return redirect(reverse("collection", kwargs={
                    "collection_id": collection_id,
                    }))
            if "2" in request.POST['response']:
                form.decline_invite(request.user, collection_id)
                message = "You have declined the invite."
            return redirect(reverse("collections"))
    return redirect(reverse("landing"))


def request_to_join_collection(request, collection_id):
    """
    TODO 
    """
    # collection = Collection.objects.get(id=collection_id)
    pass
    

""" Django Authentication """


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "jots/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "jots/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("landing"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "jots/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "jots/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "jots/register.html")


def dark_mode(request):
    """
    Dedicated to Dominique.
    """
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)

        if user.dark_mode == False:
            user.dark_mode = True
        else:
            user.dark_mode = False
        user.save()
        return redirect(reverse("collections"))
    else:
        return redirect(reverse("landing"))

def terms_of_service(request):
    return render(request, "jots/terms_of_service.html", {
        "content": utils.render_terms("jots/terms_of_service")
    })