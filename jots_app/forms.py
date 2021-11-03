from django import forms
from django.utils.safestring import mark_safe
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import send_mail

from .models import Collection, Note, Tag, Article, User
from .form_utils import *

import time
import os
""" 
1. Variables (temporary)
2. Model Forms & and related forms
3. Validation functions.
"""

""" Variables (temporary storage). Move to utils once circular import issue resolved. """


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'is_public', 'allow_public_join_requests']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 
                                        'placeholder':'Title of Collection', 
                                        'style': fanc_pants_border}),
            'description': forms.Textarea(attrs={
                                    'class': 'form-control', 
                                    'placeholder': 'Description of Collection', 
                                    'style':fanc_pants_border}),
            'is_public': forms.CheckboxInput(attrs={'style':'width:20px;height:20px;'}),
            'allow_public_join_requests': forms.CheckboxInput(attrs={'style':'width:20px;height:20px;'}),
            # 'auto_accept_all_join_requests': forms.CheckboxInput(attrs={'style':'width:20px;height:20px;'}),
        }

        labels = {
            'title': '',
            'description': '',
            'is_public': "Would you like this collection's articles and notes to be readable by the public? Only those who have joined your group may contribute.",
            'allow_public_join_requests': "Would you like to list your group as joinable by the public?",
        }
    
    @staticmethod
    def create_collection(user, form):
        if form.is_valid():
            title = standarize_titles(escape(form.cleaned_data['title']))
            collection = Collection.objects.create(
                title = title,
                description = escape(form.cleaned_data["description"]),
                leader = user,
                is_public = form.cleaned_data["is_public"],
                allow_public_join_requests = form.cleaned_data["allow_public_join_requests"],
                )

            return collection
        
    @staticmethod
    def edit_collection(user, form, collection):
        if form.is_valid() and collection.leader == user:
            collection.title = standarize_titles(escape(form.cleaned_data['title']))
            collection.description = escape(form.cleaned_data["description"])
            collection.is_public = form.cleaned_data["is_public"]
            collection.allow_public_join_requests = form.cleaned_data["allow_public_join_requests"]
            collection.save()

            return collection

    @staticmethod
    def populate_edit_collection_form(collection_id):
        collection = Collection.objects.get(id=collection_id)
        form = CollectionForm(initial={
            "title": collection.title,
            "description": collection.description,
            "is_public": collection.is_public,
            "allow_public_join_requests": collection.allow_public_join_requests,
            })
        return form


class DeleteCollectionForm(forms.Form):
    confirm = forms.BooleanField(label="Check to confirm")
    typed_confirmation = forms.CharField(required=True, 
                        label='',
                        widget=forms.TextInput(attrs={'style':fanc_pants_border,
                                                    'placeholder':'and type DELETE'    
                                                    }
                                                ))
    
    @staticmethod
    def delete_collection(collection_id, form):
        form = DeleteCollectionForm(form)
        if form.is_valid() and form.cleaned_data['typed_confirmation'] == "DELETE":
            collection = Collection.objects.get(id=collection_id)
            collection.delete()
            return "Collection Deleted"
        else:
            return "Invalid Confirmation"


class NoteForm(forms.ModelForm):
    new_tag = forms.CharField(max_length=100, 
                            required=False, 
                            label="",
                            widget=forms.TextInput(attrs={
                                'placeholder': 'or make a new tag', 
                                'style': fanc_pants_border,
                                }))

    class Meta:

        model = Note
        fields = ['text', 'tag', 'new_tag']

        widgets = {
            'text': forms.TextInput(attrs={
                                    'class': 'form-control', 
                                    'placeholder':'Take a quick note.', 
                                    'style':fanc_pants_border,
                                    'autofocus': 'autofocus',
                                    }),
            'new_tag': forms.TextInput(attrs={
                                    'placeholder':'or add a new tag',
                                       
                                    }),
            }

        labels = {
            'text': '', 
            'tag': '',
            'new_tag': '',
        }

    @staticmethod
    def create_and_return_note(collection, form, user):
        tag = TagForm.process_note_tag(form, collection.id)
        note = Note.objects.create(
                    collection = collection,
                    text = form.cleaned_data['text'],
                    tag = tag,
                    updated_by = user,
                    )
        return note
    
    @staticmethod
    def save_note_edit(note, form, user):
        tag = TagForm.process_note_tag(form, note.collection.id)
        note.text = form.cleaned_data['text']
        note.updated_by = user
        if tag != None:
            note.tag = tag
        note.save()



class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={
                                    # 'class': 'form-control', 
                                    'max_length': '100',
                                    'placeholder': 'Create a new tag.', 
                                    'style':fanc_pants_border
                                    }),
                    }

        labels = {
            'name': '',
        }

    @staticmethod
    def process_new_tag(collection_id, form):
        if form.is_valid():
            tag_name = standarize_titles(escape(form.cleaned_data['name']))
            tag = TagForm.save_new_tag_or_get_tag(tag_name, collection_id)
    
    @staticmethod
    def save_tag_edit(collection_id, form):
        if form.is_valid():
            old_tag_name = form.cleaned_data['old_tag']
            tag = Tag.objects.get(collection=collection_id, name=old_tag_name)
            new_tag_name = standarize_titles(escape(form.cleaned_data['name']))
            if not Tag.objects.filter(name=new_tag_name, 
                                        collection=collection_id).exists():
                tag.name = new_tag_name
                tag.save()
                return "Successfully edited."
            else:
                return "Error: that tagname already exists."

    @staticmethod
    def process_note_tag(form, collection_id):
        """
        Returns a selected/created new tag from NoteForm posts. 
        """
        if form.cleaned_data['new_tag']:
            tag_name = standarize_titles(escape(form.cleaned_data['new_tag']))
            tag = TagForm.save_new_tag_or_get_tag(tag_name, collection_id)
        
        elif form.cleaned_data['tag']:
            tag = form.cleaned_data['tag']

        else:
            tag = None # No tag-related user input.

        return tag

    
    @staticmethod
    def process_article_tag(form, collection_id, title):

        if form.cleaned_data['new_tag']:
            tag = standarize_titles(escape(form.cleaned_data['new_tag']))
            tag = TagForm.save_new_tag_or_get_tag(tag, collection_id)

        elif form.cleaned_data['tag']:
            tag = form.cleaned_data['tag']

        elif form.cleaned_data['auto_create_tag']:
            tag = TagForm.save_new_tag_or_get_tag(title, 
                                                collection_id)
        else:
            tag = None # No tag-related user input.

        return tag


    @staticmethod 
    def save_new_tag_or_get_tag(tag_name, collection_id):
        """
        Saves a new tag to the database. 
        If tag already exists, returns that tag.
        """
        if not Tag.objects.filter(name=tag_name, collection=collection_id).exists(): 
            tag = TagForm.save_tag(tag_name, collection_id)
        else:
            tag = Tag.objects.get(name=tag_name, collection=collection_id)
        
        return tag

    @staticmethod
    def save_tag(tag_name, collection_id):
        tag = Tag.objects.create(name=tag_name, 
                                collection=Collection.objects.get(id=collection_id))
        return tag
    
    @staticmethod
    def delete_tag(collection_id, form):
        if form.is_valid(): 
            tag_name = form.cleaned_data['tag']
            tag = Tag.objects.filter(collection=collection_id, name=tag_name)
            tag.delete()
            return "Successfully Deleted"
        else:
            return "Invalid submission"


class EditTagForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'New name for tag'}))

    labels = {
        'oldtag': '',
        'name': '',
    }


class DeleteTagForm(forms.Form):
    pass


class ArticleForm(forms.ModelForm):
    new_tag = forms.CharField(max_length=100, 
                        required=False, 
                        label="",
                        widget=forms.TextInput(attrs={
                            'placeholder': 'or create a new tag', 
                            'style': fanc_pants_border,
                            }))
    auto_create_tag = forms.BooleanField(required=False, label="or Auto-Tag:")
    content = forms.CharField(label="",
                            widget=forms.Textarea(attrs={
                                'class': 'form-control', 
                                'placeholder': example_markdown, 
                                'style':fanc_pants_border
                            }))

    class Meta:
        model = Article
        fields = ['title', 'tag', 'new_tag', 'auto_create_tag', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                                    'class': 'form-control', 
                                    'placeholder':'Title.', 
                                    'style':fanc_pants_border
                                    }),
        }
      
        labels = {
            'title': '',
            'tag': '',
        }
    
    @staticmethod
    def create_and_return_article(collection_id, user, form):
        collection = Collection.objects.get(pk=collection_id)

        if form.is_valid():
            title = ArticleForm.process_article_title(form.cleaned_data['title'], collection_id)
        
            tag = TagForm.process_article_tag(form, collection_id, title)
            slug = ArticleForm.slugify_article(collection_id, title)
            ArticleForm.save_article_as_md(slug, form.cleaned_data['content'])

            article = Article.objects.create(
                            collection = Collection.objects.get(id=collection_id),
                            title = title,
                            tag = tag,
                            content_slug = slug, 
                            created_by = user,
                            updated_by = user,
                            )

            return article
           
    @staticmethod
    def edit_article(article, form, user):
        tag = TagForm.process_article_tag(form, article.collection.id, article.title)

        with open(f"articles/{article.content_slug}.md", "w") as f:
            f.write(form.cleaned_data['content'])

        title = form.cleaned_data['title']
        if title != article.title:
            article.title = ArticleForm.process_article_title(title, article.collection.id)
        article.updated_by = user

        if tag != None:
            article.tag = tag

        article.save()

    @staticmethod
    def append_note(article, note_id):
        note = Note.objects.get(pk=note_id)

        with open (f'articles/{article.content_slug}.md', 'a') as f:
            f.write(f'\n * {note.text}')

    @staticmethod
    def slugify_article(collection_id, title):
        collection = Collection.objects.get(id=collection_id)
        slug = f"{collection.id}{title}{time.time()}"
        slug = slug.replace(" ", "-")
        slug = slug.replace("'", "-")
        slug = slug.replace(".", "-")
        return slug

    @staticmethod
    def save_article_as_md(slug, content):
        filename = f"articles/{slug}.md"
        if default_storage.exists(filename):
            default_storage.delete(filename)
        default_storage.save(filename, ContentFile(content))
    
    @staticmethod
    def process_article_title(title, collection_id):
        # TODO: get a more standard titling system, using regex
        title = standarize_titles(escape(title))
        article_copies = 0 
        while ArticleForm.article_exists(title, collection_id):
            article_copies += 1
            title += str(article_copies)
        
        return title

    @staticmethod
    def article_exists(title, collection_id):
        existing_titles = Article.objects.filter(collection=collection_id).values_list('title', flat=True)
        if title in existing_titles:
                return True



class EditArticleForm(ArticleForm):
    
    class Meta:
        model = Article
        fields = ['title', 'tag', 'content']

class DeleteArticleForm(DeleteCollectionForm):

    @staticmethod
    def delete_article(article_id, form):
        form = DeleteArticleForm(form)
        if form.is_valid() and form.cleaned_data['typed_confirmation'] == "DELETE":
            article = Article.objects.get(id=article_id)
            if os.path.exists(f"article/{article.content_slug}.md"):
                os.remove("demofile.txt")
            article.delete()
            return "Article Deleted"
        else:
            return "Invalid Confirmation"


""" Invites | Join Requests |  Feedback """

class InviteToJotsForm(forms.Form):
    email = forms.EmailField(label='', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email of the person you would like to invite to jots', 'class': 'form-control'}))

    def email_invite_to_jots(self, user, collection_title, sendee):
        """
        Email invite to a collection
        """
        nl = "\n"
        send_mail(
            f"You Have Been Invited by {user.username}",
            f"You have been invited by {user.username} to use jots.com. To join {user.username}'s {collection_title}, you must register at jots.com/register and then provide {user.username} with your new username. {nl}{nl} To learn more, visit jots.com. {nl} {nl} If you weren't expecting this email, please forward it to journalofthesession@gmail.com.",
            user.email,
            [sendee],
            fail_silently=False,
            )


class InviteToGroupForm(forms.Form):

    user = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Enter username to invite to group', 'class': 'form-control'}))

    def handle_invite(self, collection_object, username):
        try:
            user = User.objects.get(username=username)
            if user:
                user.collection_invites.add(collection_object)
                user.save()
            else:
                return True
        except User.DoesNotExist:
            # for security, doesn't show if the user doesn't exist.
            return True


class AcceptGroupInviteForm(forms.Form):
    CHOICES = [('1', 'Accept'), ('2', 'Decline')]
    response = forms.ChoiceField(choices=CHOICES, 
                    widget=forms.RadioSelect(attrs={'class': 'radio'}),
                    label='')
    
    @staticmethod
    def accept_invite(user, collection_id):
        collection = Collection.objects.get(id=collection_id)
        collection.followers.add(user)
        collection.save()
        user.collection_invites.remove(collection)
        user.save()

    @staticmethod
    def decline_invite(user, collection_id):
        collection = Collection.objects.get(id=collection_id)
        user.collection_invites.remove(collection)
        user.save()


class FeedbackForm(forms.Form):
    name = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Your name', 
                                                        'style':fanc_pants_border}))
    message = forms.CharField(label="", widget=forms.Textarea(attrs={'class': 'form-control', 
                                                        'style':fanc_pants_border,
                                                        'placeholder': 'Feature requests or bug reports. Please be as detailed as you reasonably can. It helps me find the bugs and solve them.'}))


    def email_feedback(self, user, name, message):
        send_mail(
            f"Feedback from {name}, AKA, {user.username}",
            f"{message} . . . – {user.username}, {user.email}",
            user.email,
            ['journalofthesession@gmail.com'],
            fail_silently=False,
        )