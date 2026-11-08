from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import RegisterForm, ProfileForm, MessageForm
from .models import Chat, Contact, Message, Profile


def ensure_profile(user):
    Profile.objects.get_or_create(user=user)


def register_view(request):
    if request.user.is_authenticated: return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(); ensure_profile(user); login(request, user)
        return redirect('home')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    ensure_profile(request.user)
    Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
    query = request.GET.get('q','').strip()
    contacts = Contact.objects.filter(owner=request.user).select_related('person','person__profile')
    if query:
        contacts = contacts.filter(Q(person__username__icontains=query) | Q(person__first_name__icontains=query))
    chats = request.user.chats.prefetch_related('participants','messages').order_by('-updated_at')
    users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query)).exclude(pk=request.user.pk)[:8] if query else []
    for person in users:
        ensure_profile(person)
    for contact in contacts:
        ensure_profile(contact.person)
    return render(request, 'chat/home.html', {'contacts':contacts,'chats':chats,'users':users,'query':query,'all_users':User.objects.exclude(pk=request.user.pk).order_by('username')})


@login_required
def add_contact(request, user_id):
    person = get_object_or_404(User, pk=user_id)
    if person != request.user:
        Contact.objects.get_or_create(owner=request.user, person=person)
        chat = None
        for candidate in request.user.chats.filter(chat_type=Chat.DIRECT):
            ids = set(candidate.participants.values_list('id', flat=True))
            if ids == {request.user.id, person.id}: chat = candidate; break
        if chat is None:
            chat = Chat.objects.create(chat_type=Chat.DIRECT); chat.participants.add(request.user, person)
        return redirect('chat_detail', chat_id=chat.id)
    return redirect('home')


@login_required
def create_chat(request):
    if request.method != 'POST': return redirect('home')
    title = request.POST.get('title','').strip()[:100]
    kind = request.POST.get('chat_type', Chat.GROUP)
    ids = {int(x) for x in request.POST.getlist('participants') if x.isdigit()}
    ids.add(request.user.id)
    if kind not in (Chat.GROUP, Chat.CHANNEL): kind = Chat.GROUP
    if kind == Chat.GROUP and len(ids) < 3:
        messages.error(request, 'Для группы выбери минимум двух других участников (всего 3 человека).')
        return redirect('home')
    if kind == Chat.CHANNEL and not title:
        messages.error(request, 'Укажи название канала.')
        return redirect('home')
    chat = Chat.objects.create(title=title or 'Новая группа', chat_type=kind, is_group=(kind == Chat.GROUP))
    chat.participants.set(User.objects.filter(id__in=ids))
    chat.admins.add(request.user)
    messages.success(request, 'Канал создан.' if kind == Chat.CHANNEL else 'Группа создана.')
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id, participants=request.user)
    ensure_profile(request.user)
    Profile.objects.filter(user=request.user).update(last_seen=timezone.now())
    form = MessageForm(request.POST or None,request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        if chat.chat_type == Chat.CHANNEL and not chat.admins.filter(pk=request.user.pk).exists():
            messages.error(request, 'Писать в канал могут только администраторы.')
            return redirect('chat_detail', chat_id=chat.id)
        message = form.save(commit=False)
        message.chat = chat
        message.sender = request.user
        message.save()

        chat.save()
        return redirect('chat_detail', chat_id=chat.id)

    other_users = chat.participants.exclude(pk=request.user.pk).select_related('profile')
    title = chat.title or ', '.join(u.username for u in other_users) or 'Избранное'
    return render(request, 'chat/detail.html', {'chat':chat,'chat_title':title,'other_users':other_users,'form':form,'messages_list':chat.messages.select_related('sender','forwarded_from','forwarded_from__sender'),'forward_targets':request.user.chats.exclude(pk=chat.pk).order_by('title')})

@login_required
def forward_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, chat__participants=request.user)
    if request.method == 'POST':
        target_id = request.POST.get('target_chat')
        target = get_object_or_404(Chat, pk=target_id, participants=request.user)
        if target.chat_type != Chat.CHANNEL or target.admins.filter(pk=request.user.pk).exists():
            new_message = Message(
                chat=target,
                sender=request.user,
                body=message.body,
                forwarded_from=message
            )

            if message.attachment:
                new_message.attachment = message.attachment.name

            new_message.save()
            target.save()
            target.save()
            messages.success(request, 'Сообщение переслано.')
        else:
            messages.error(request, 'В этот канал могут отправлять сообщения только администраторы.')
        return redirect('chat_detail', chat_id=message.chat_id)
    return redirect('chat_detail', chat_id=message.chat_id)

@login_required
def profile_view(request):
    ensure_profile(request.user)
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request, 'Профиль сохранён.'); return redirect('profile')
    return render(request, 'chat/profile.html', {'form':form})

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, sender=request.user, chat__participants=request.user)
    if request.method == 'POST' and request.POST.get('body','').strip():
        message.body = request.POST['body'].strip()[:5000]; message.edited_at = timezone.now(); message.save(update_fields=['body','edited_at'])
    return redirect('chat_detail', chat_id=message.chat_id)

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id, sender=request.user, chat__participants=request.user)
    chat_id = message.chat_id
    if request.method == 'POST': message.delete()
    return redirect('chat_detail', chat_id=chat_id)
