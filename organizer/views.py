"""
DCTFd - A Capture The Flag platform built with Django

This file is part of the DCTFd project.

Developed by Srivatsan Sk
MIT License - Copyright (c) 2025 Srivatsan Sk
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.db import models
import json

from challenges.models import Challenge, ChallengeCategory, Submission, Hint, Flag, ChallengeFile
from event.models import Event
from teams.models import Team
from users.models import BaseUser
from .forms import EventForm, ChallengeForm
from superadmin.forms import ChallengeCategoryForm

# Alias BaseUser as User for clarity in code
User = BaseUser

def organizer_required(view_func):
    """Decorator to ensure only organizers can access views"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_organizer:
            messages.error(request, _('You do not have permission to access this page.'))
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@organizer_required
def dashboard(request):
    """Organizer dashboard view with summary statistics"""
    # Get counts for dashboard stats
    challenge_count = Challenge.objects.count()
    team_count = Team.objects.count()
    user_count = BaseUser.objects.filter(type='user').count()
    submission_count = Submission.objects.count()
    correct_submission_count = Submission.objects.filter(is_correct=True).count()
    
    # Get current event - single event system
    current_event = Event.objects.first()
    if not current_event:
        # Create default event if none exists
        from django.utils import timezone
        from django.conf import settings
        from django.utils.text import slugify
        current_event = Event.objects.create(
            name=settings.EVENT_NAME,
            slug=slugify(settings.EVENT_NAME),
            description=f"{settings.EVENT_NAME} CTF Event",
            short_description=f"{settings.EVENT_NAME} CTF Event",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(days=30),
            registration_start=timezone.now(),
            registration_end=timezone.now() + timezone.timedelta(days=30),
            status='running',
            is_visible=True
        )
    
    # Get top teams with scores and solve counts
    top_teams = Team.objects.annotate(
        solve_count=Count('submissions', filter=Q(submissions__is_correct=True))
    ).order_by('-score', '-solve_count')[:5]
    
    # Recent submissions
    recent_submissions = Submission.objects.select_related(
        'user', 'team', 'challenge'
    ).order_by('-submitted_at')[:10]
    
    # Challenge statistics
    challenge_stats = Challenge.objects.annotate(
        solve_count=Count('submissions', filter=Q(submissions__is_correct=True)),
        total_submission_count=Count('submissions')
    ).select_related('category')
    
    # Calculate solve percentages and first blood for each challenge
    for challenge in challenge_stats:
        if challenge.total_submission_count > 0:
            challenge.solve_percentage = round((challenge.solve_count / team_count) * 100, 1) if team_count > 0 else 0
        else:
            challenge.solve_percentage = 0
            
        # Get first blood (first correct submission)
        first_submission = Submission.objects.filter(
            challenge=challenge, 
            is_correct=True
        ).select_related('team', 'user').order_by('submitted_at').first()
        
        if first_submission:
            challenge.first_blood = first_submission
            challenge.first_blood.solved_at = first_submission.submitted_at
        else:
            challenge.first_blood = None
    
    context = {
        'challenge_count': challenge_count,
        'team_count': team_count,
        'user_count': user_count,
        'submission_count': submission_count,
        'correct_submission_count': correct_submission_count,
        'top_teams': top_teams,
        'recent_submissions': recent_submissions,
        'challenge_stats': challenge_stats,
        'current_event': current_event,
    }
    
    return render(request, 'organizer/dashboard.html', context)

@login_required
@organizer_required
def events(request):
    """List all events"""
    events = Event.objects.all().order_by('-start_time')
    return render(request, 'organizer/events/list.html', {'events': events})

@login_required
@organizer_required
def create_event(request):
    """Create a new event"""
    # Placeholder for now, will implement form handling
    return render(request, 'organizer/events/create.html')

@login_required
@organizer_required
def edit_event(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'organizer/events/edit.html', {'event': event})

@login_required
@organizer_required
def challenges(request):
    """List all challenges"""
    # Annotate challenges with solve counts
    challenges = Challenge.objects.annotate(
        solve_count=Count("submissions", filter=Q(submissions__is_correct=True)),
        prerequisite_count=Count("prerequisites", distinct=True),
        unlock_count=Count("unlocks", distinct=True),
    ).order_by("-created_at")

    # Annotate categories with challenge counts
    categories = ChallengeCategory.objects.annotate(
        challenge_count=Count('challenges')
    ).order_by('name')

    # Organize challenges by category with solve counts
    challenges_by_category = {}
    for category in categories:
        category_challenges = challenges.filter(category=category)
        challenges_by_category[category] = category_challenges

    # Include challenges without a category
    uncategorized = challenges.filter(category__isnull=True)
    if uncategorized.exists():
        # Create a dummy category object for uncategorized
        class UncategorizedCategory:
            name = "Uncategorized"
            slug = "uncategorized"
            color = "#6c757d"

        challenges_by_category[UncategorizedCategory()] = uncategorized

    return render(request, 'organizer/challenges/list.html', {
        'challenges': challenges,
        'categories': categories,
        'challenges_by_category': challenges_by_category
    })

@login_required
@organizer_required
def create_challenge(request):
    """Create a new challenge"""
    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            challenge = form.save(commit=False)
            # Automatically assign the default event
            default_event = Event.objects.first()
            if not default_event:
                # Create a default event if none exists
                from django.utils import timezone
                from django.conf import settings
                from django.utils.text import slugify
                default_event = Event.objects.create(
                    name=settings.EVENT_NAME,
                    slug=slugify(settings.EVENT_NAME),
                    description=f"{settings.EVENT_NAME} CTF Event",
                    short_description=f"{settings.EVENT_NAME} CTF Event",
                    start_time=timezone.now(),
                    end_time=timezone.now() + timezone.timedelta(days=30),
                    registration_start=timezone.now(),
                    registration_end=timezone.now() + timezone.timedelta(days=30),
                    status='running',
                    is_visible=True
                )
            challenge.event = default_event
            challenge.save()

            # Save the prerequisites
            form.save_m2m()

            # Process flags
            flag_counter = 1
            while f'flag_{flag_counter}' in request.POST:
                flag_value = request.POST.get(f'flag_{flag_counter}')
                flag_type = request.POST.get(f'flag_type_{flag_counter}', 'static')

                if flag_value:
                    from challenges.models import Flag
                    Flag.objects.create(
                        challenge=challenge,
                        flag=flag_value,
                        type=flag_type
                    )
                flag_counter += 1

            # Process hints
            hint_counter = 1
            while f'hint_{hint_counter}' in request.POST:
                hint_content = request.POST.get(f'hint_{hint_counter}')
                hint_cost = request.POST.get(f'hint_cost_{hint_counter}', 0)

                if hint_content:
                    Hint.objects.create(
                        challenge=challenge,
                        content=hint_content,
                        cost=int(hint_cost) if hint_cost else 0
                    )
                hint_counter += 1

            # Process file uploads
            files = request.FILES.getlist('new_files')
            file_visibilities = request.POST.getlist('new_file_visible')

            for i, file in enumerate(files):
                if file:
                    from challenges.models import ChallengeFile
                    is_visible = i < len(file_visibilities)
                    ChallengeFile.objects.create(
                        challenge=challenge,
                        file=file,
                        is_visible=is_visible
                    )

            messages.success(request, _('Challenge "{}" created successfully.').format(challenge.name))
            return redirect('organizer:challenge_detail', challenge_id=challenge.id)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ChallengeForm()

    categories = ChallengeCategory.objects.all()
    events = Event.objects.all()

    return render(request, 'organizer/challenges/create.html', {
        'form': form,
        'categories': categories,
        'events': events
    })

@login_required
@organizer_required
def edit_challenge(request, challenge_id):
    """Edit an existing challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == 'POST':
        form = ChallengeForm(request.POST, request.FILES, instance=challenge)
        if form.is_valid():
            challenge = form.save(commit=False)
            # Preserve the original event
            if not challenge.event:
                default_event = Event.objects.first()
                if not default_event:
                    # Create a default event if none exists
                    from django.utils import timezone
                    from django.conf import settings
                    from django.utils.text import slugify
                    default_event = Event.objects.create(
                        name=settings.EVENT_NAME,
                        slug=slugify(settings.EVENT_NAME),
                        description=f"{settings.EVENT_NAME} CTF Event",
                        short_description=f"{settings.EVENT_NAME} CTF Event",
                        start_time=timezone.now(),
                        end_time=timezone.now() + timezone.timedelta(days=30),
                        registration_start=timezone.now(),
                        registration_end=timezone.now() + timezone.timedelta(days=30),
                        status='running',
                        is_visible=True
                    )
                challenge.event = default_event
            challenge.save()

            # Save the prerequisites
            form.save_m2m()

            # Process existing flags
            for flag in challenge.flags.all():
                flag_value = request.POST.get(f'flag_{flag.id}')
                flag_type = request.POST.get(f'flag_type_{flag.id}', 'static')

                if flag_value:
                    flag.flag = flag_value
                    flag.type = flag_type
                    flag.save()

            # Process new flags
            flag_counter = 1
            while f'flag_{flag_counter}' in request.POST:
                # Skip if this is an existing flag
                if not challenge.flags.filter(id=flag_counter).exists():
                    flag_value = request.POST.get(f'flag_{flag_counter}')
                    flag_type = request.POST.get(f'flag_type_{flag_counter}', 'static')

                    if flag_value:
                        from challenges.models import Flag
                        Flag.objects.create(
                            challenge=challenge,
                            flag=flag_value,
                            type=flag_type
                        )
                flag_counter += 1

            # Process existing hints
            for hint in challenge.hints.all():
                hint_content = request.POST.get(f'hint_{hint.id}')
                hint_cost = request.POST.get(f'hint_cost_{hint.id}', 0)

                if hint_content:
                    hint.content = hint_content
                    hint.cost = int(hint_cost) if hint_cost else 0
                    hint.save()

            # Process new hints
            hint_counter = 1
            while f'hint_{hint_counter}' in request.POST:
                # Skip if this is an existing hint
                if not challenge.hints.filter(id=hint_counter).exists():
                    hint_content = request.POST.get(f'hint_{hint_counter}')
                    hint_cost = request.POST.get(f'hint_cost_{hint_counter}', 0)

                    if hint_content:
                        Hint.objects.create(
                            challenge=challenge,
                            content=hint_content,
                            cost=int(hint_cost) if hint_cost else 0
                        )
                hint_counter += 1

            # Process file deletions
            for file in challenge.challenge_files.all():
                if request.POST.get(f'delete_file_{file.id}'):
                    file.delete()
                else:
                    # Update visibility
                    is_visible = request.POST.get(f'file_visible_{file.id}') == 'on'
                    file.is_visible = is_visible
                    file.save()

            # Process new file uploads
            files = request.FILES.getlist('new_files')
            file_visibilities = request.POST.getlist('new_file_visible')

            for i, file in enumerate(files):
                if file:
                    from challenges.models import ChallengeFile
                    is_visible = i < len(file_visibilities)
                    ChallengeFile.objects.create(
                        challenge=challenge,
                        file=file,
                        is_visible=is_visible
                    )

            messages.success(request, _('Challenge "{}" updated successfully.').format(challenge.name))
            return redirect('organizer:challenge_detail', challenge_id=challenge.id)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ChallengeForm(instance=challenge)

    categories = ChallengeCategory.objects.all()
    events = Event.objects.all()

    return render(request, 'organizer/challenges/edit.html', {
        'form': form,
        'challenge': challenge,
        'categories': categories,
        'events': events
    })

@login_required
@organizer_required
def teams(request):
    """List all teams"""
    teams = Team.objects.annotate(
        solved_count=Count(
            "submissions__challenge",
            filter=Q(submissions__is_correct=True),
            distinct=True,
        )
    ).order_by("-score")
    return render(request, 'organizer/teams/list.html', {'teams': teams})

@login_required
@organizer_required
def users(request):
    """List all users"""
    users = BaseUser.objects.filter(type='user').order_by('username')
    return render(request, 'organizer/users/list.html', {'users': users})

@login_required
@organizer_required
def submissions(request):
    """List all submissions"""
    submissions = Submission.objects.select_related(
        'user', 'team', 'challenge'
    ).order_by('-submitted_at')
    return render(request, 'organizer/submissions/list.html', {'submissions': submissions})


@login_required
@organizer_required
def setup_ctf(request):
    """Set up a new CTF event"""
    # Check if an event already exists
    existing_event = Event.objects.first()
    
    if request.method == "POST":
        if existing_event:
            form = EventForm(request.POST, request.FILES, instance=existing_event)
        else:
            form = EventForm(request.POST, request.FILES)
        
        if form.is_valid():
            event = form.save()
            
            # Update the EVENT_NAME setting in memory
            from django.conf import settings
            settings.EVENT_NAME = event.name
            
            messages.success(request, _("CTF event has been set up successfully."))
            return redirect("organizer:dashboard")
    else:
        # Pre-fill with settings value if creating new
        if existing_event:
            form = EventForm(instance=existing_event)
        else:
            from django.conf import settings
            initial_data = {
                'name': settings.EVENT_NAME,
            }
            form = EventForm(initial=initial_data)

    return render(request, "organizer/setup_ctf.html", {"form": form})


@login_required
@organizer_required
def reset_ctf(request):
    """Reset the CTF event (clear submissions and scores)"""
    if request.method == "POST":
        # Logic to reset CTF event
        messages.success(request, _("CTF event has been reset successfully."))
        return redirect("organizer:dashboard")

    return render(request, "organizer/reset_ctf.html")


@login_required
@organizer_required
def settings(request):
    """CTF event settings"""
    # Get the current active event or first event
    event = Event.objects.first()

    # In a single event setup, we'll use the first event's settings
    context = {"event": event}

    return render(request, "organizer/settings.html", context)


@login_required
@organizer_required
def scoreboard(request):
    """CTF scoreboard"""
    # Get teams ordered by score for scoreboard
    teams = Team.objects.all().order_by("-score")

    # Get some stats for the scoreboard
    total_teams = teams.count()
    total_challenges = Challenge.objects.count()
    total_solves = Submission.objects.filter(is_correct=True).count()

    context = {
        "teams": teams,
        "total_teams": total_teams,
        "total_challenges": total_challenges,
        "total_solves": total_solves,
    }

    return render(request, "organizer/scoreboard/list.html", context)


@login_required
@organizer_required
def category_create(request):
    """Create a new challenge category"""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")

        if name:
            category = ChallengeCategory.objects.create(
                name=name, description=description
            )
            messages.success(request, _(f'Category "{name}" created successfully.'))
            return redirect("organizer:challenges")
        else:
            messages.error(request, _("Category name is required."))

    return redirect("organizer:challenges")


@login_required
@organizer_required
def challenge_delete(request, challenge_id):
    """Delete a challenge - Restricted to admin users only"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        # Check if user is an admin
        if request.user.is_admin:
            challenge_name = challenge.name
            challenge.delete()
            messages.success(
                request, _(f'Challenge "{challenge_name}" deleted successfully.')
            )
        else:
            messages.error(
                request, _('Only administrators can delete challenges.')
            )

    return redirect("organizer:challenges")


@login_required
@organizer_required
def toggle_challenge_visibility(request, challenge_id):
    """Toggle challenge visibility (hide/unhide)"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        # Toggle visibility
        challenge.is_visible = not challenge.is_visible
        challenge.save()
        
        if challenge.is_visible:
            messages.success(
                request, _(f'Challenge "{challenge.name}" is now visible.')
            )
        else:
            messages.success(
                request, _(f'Challenge "{challenge.name}" is now hidden.')
            )

    return redirect("organizer:challenges")


@login_required
@organizer_required
def challenges_import(request):
    """Import challenges from JSON file"""
    from utils.validators import validate_challenge_import_json
    from django.utils.encoding import force_str
    
    if request.method == "POST" and request.FILES.get("import_file"):
        import_file = request.FILES["import_file"]
        import_results = {
            'filename': import_file.name,
            'filesize': import_file.size,
            'success': False,
            'challenges_total': 0,
            'challenges_imported': 0,
            'errors': [],
            'categories_created': [],
            'imported_challenges': []
        }

        # Check file extension and content type
        content_type = import_file.content_type
        is_json = import_file.name.endswith('.json') and content_type in ['application/json', 'text/plain']
        
        if not is_json:
            import_results['errors'].append({
                'type': 'file_format',
                'message': force_str(_("Only JSON files are supported for import. Please check file extension and content type."))
            })
            request.session['import_results'] = import_results
            return redirect("organizer:challenges_import_results")

        try:
            # Parse JSON content
            try:
                import_data = json.loads(import_file.read().decode("utf-8"))
            except json.JSONDecodeError as e:
                import_results['errors'].append({
                    'type': 'json_parse',
                    'message': force_str(_(f"Invalid JSON format: {str(e)}"))
                })
                request.session['import_results'] = import_results
                return redirect("organizer:challenges_import_results")
            
            # Validate JSON structure and challenge data
            is_valid, validation_results = validate_challenge_import_json(import_data)
            
            # Convert any translation proxies to strings for JSON serialization
            if 'errors' in validation_results:
                for error in validation_results['errors']:
                    if 'message' in error:
                        error['message'] = force_str(error['message'])
                    if 'errors' in error:
                        for field_error in error['errors']:
                            if 'message' in field_error:
                                field_error['message'] = force_str(field_error['message'])
            
            if not is_valid:
                import_results.update(validation_results)
                request.session['import_results'] = import_results
                return redirect("organizer:challenges_import_results")
            
            # Start import process for valid challenges
            import_results.update(validation_results)
            
            # Import categories first if they exist
            categories_created = []
            if "categories" in import_data:
                for category_data in import_data["categories"]:
                    category_name = category_data.get("name")
                    if not category_name:
                        continue
                        
                    category, created = ChallengeCategory.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'description': category_data.get("description", ""),
                            'color': category_data.get("color", "#007bff")
                        }
                    )
                    if created:
                        categories_created.append(category_name)
            
            import_results['categories_created'] = categories_created
            
            # Process each valid challenge
            imported_count = 0
            imported_challenges = []
            
            for challenge_data in validation_results['valid_challenges']:
                # Get or create category
                category_name = challenge_data.get("category", "Uncategorized")
                category, created = ChallengeCategory.objects.get_or_create(
                    name=category_name,
                    defaults={'color': '#007bff'}
                )
                if created and category_name not in categories_created:
                    categories_created.append(category_name)

                # Get default event - this will be used for all challenges
                default_event = Event.objects.first()
                if not default_event:
                    # Create a default event if none exists
                    from django.utils import timezone
                    from django.conf import settings
                    from django.utils.text import slugify
                    default_event = Event.objects.create(
                        name=settings.EVENT_NAME,
                        slug=slugify(settings.EVENT_NAME),
                        description=f"{settings.EVENT_NAME} CTF Event",
                        short_description=f"{settings.EVENT_NAME} CTF Event",
                        start_time=timezone.now(),
                        end_time=timezone.now() + timezone.timedelta(days=30),
                        registration_start=timezone.now(),
                        registration_end=timezone.now() + timezone.timedelta(days=30),
                        status='running',
                        is_visible=True
                    )
                    
                # Create challenge
                challenge = Challenge.objects.create(
                    name=challenge_data.get("name"),
                    description=challenge_data.get("description", ""),
                    category=category,
                    difficulty=challenge_data.get("difficulty", 1),
                    value=challenge_data.get("value", challenge_data.get("points", 100)),
                    max_attempts=challenge_data.get("max_attempts", 0),
                    type=challenge_data.get("type", "standard"),
                    state=challenge_data.get("state", "visible"),
                    is_visible=challenge_data.get("is_visible", True),
                    author=challenge_data.get("author", request.user.username),
                    event=default_event  # Use the default event for all challenges
                )
                
                # Add flags
                flags_data = challenge_data.get("flags", [])
                flags_created = []
                for flag_data in flags_data:
                    flag = Flag.objects.create(
                        challenge=challenge,
                        flag=flag_data.get("flag", ""),
                        type=flag_data.get("type", "static")
                    )
                    flags_created.append(flag.flag)
                
                # Add hints
                hints_data = challenge_data.get("hints", [])
                hints_created = []
                for hint_data in hints_data:
                    if isinstance(hint_data, str):
                        # Support legacy string format
                        hint = Hint.objects.create(
                            challenge=challenge,
                            content=hint_data,
                            cost=0
                        )
                        hints_created.append({"content": hint_data, "cost": 0})
                    else:
                        hint = Hint.objects.create(
                            challenge=challenge,
                            content=hint_data.get("content", ""),
                            cost=hint_data.get("cost", 0)
                        )
                        hints_created.append({"content": hint_data.get("content", ""), "cost": hint_data.get("cost", 0)})

                imported_count += 1
                imported_challenges.append({
                    'id': challenge.id,
                    'name': challenge.name,
                    'category': category_name,
                    'difficulty': challenge.difficulty,
                    'value': challenge.value,
                    'flags_count': len(flags_created),
                    'hints_count': len(hints_created)
                })

            import_results['challenges_imported'] = imported_count
            import_results['imported_challenges'] = imported_challenges
            import_results['success'] = imported_count > 0
            
            request.session['import_results'] = import_results
            return redirect("organizer:challenges_import_results")
            
        except Exception as e:
            import_results['errors'].append({
                'type': 'unexpected',
                'message': force_str(_(f"Error importing challenges: {str(e)}"))
            })
            request.session['import_results'] = import_results
            return redirect("organizer:challenges_import_results")

    return redirect("organizer:challenges")


@login_required
@organizer_required
def download_challenge_template(request):
    """Download a sample challenge template"""
    template_data = {
        "format_version": "1.0",
        "challenges": [
            {
                "name": "Sample Web Challenge",
                "description": "This is a sample web challenge. Participants need to find the flag by exploiting a web vulnerability.\n\n**Instructions:**\n1. Visit the challenge website\n2. Find the vulnerability\n3. Exploit it to get the flag\n\n**Hint:** Look for common web vulnerabilities like SQL injection or XSS.",
                "category": "Web",
                "difficulty": 2,
                "value": 150,
                "type": "standard",
                "state": "visible",
                "is_visible": True,
                "author": "Admin",
                "flags": [
                    {
                        "flag": "flag{sample_web_challenge_flag}",
                        "type": "static"
                    },
                    {
                        "flag": "flag{alternative_.*_solution}",
                        "type": "regex"
                    }
                ],
                "hints": [
                    {
                        "content": "Try looking at the page source code for clues",
                        "cost": 10
                    },
                    {
                        "content": "The vulnerability might be in the user input fields",
                        "cost": 25
                    }
                ],
                "max_attempts": 10,
                "connection_info": "http://web-challenge.ctf.local:8080",
                "flag_logic": "any"
            },
            {
                "name": "Sample Crypto Challenge",
                "description": "Decrypt the given ciphertext to find the flag.\n\nCiphertext: `Uryyb Jbeyq! Guvf vf n fvzcyr EBG13 rapelcgvba.`\n\n**Note:** The flag format is flag{...}",
                "category": "Crypto",
                "difficulty": 1,
                "value": 100,
                "type": "static",
                "state": "visible",
                "flags": [
                    {
                        "flag": "flag{hello_world_rot13}",
                        "type": "static"
                    }
                ],
                "hints": [
                    {
                        "content": "This is a simple substitution cipher",
                        "cost": 5
                    },
                    {
                        "content": "ROT13 is a Caesar cipher with a shift of 13",
                        "cost": 15
                    }
                ],
                "max_attempts": 0
            },
            {
                "name": "Sample Forensics Challenge", 
                "description": "Analyze the network traffic to find the hidden flag.\n\n**Task:** Examine the provided information to discover the flag.\n\n**Tools you might need:**\n- Wireshark\n- tcpdump\n- strings\n\n**Note:** The flag is hidden somewhere in the provided information.",
                "category": "Forensics",
                "difficulty": 3,
                "value": 200,
                "type": "static",
                "state": "visible",
                "flags": [
                    {
                        "flag": "flag{network_forensics_master}",
                        "type": "static"
                    }
                ],
                "hints": [
                    {
                        "content": "Look for unusual protocol usage or data patterns",
                        "cost": 20
                    },
                    {
                        "content": "The data might be encoded or hidden in the content",
                        "cost": 40
                    }
                ],
                "max_attempts": 5
            },
            {
                "name": "Sample Quiz Challenge",
                "description": "Answer this cybersecurity knowledge question correctly.\n\n**Question:** What is the default port number for HTTPS?\n\nA) 80\nB) 443\nC) 8080\nD) 8443\n\n**Instructions:** Submit the flag in the format flag{answer_letter} (e.g., flag{A})",
                "category": "Misc",
                "difficulty": 1,
                "value": 50,
                "type": "static",
                "state": "visible",
                "flags": [
                    {
                        "flag": "flag{B}",
                        "type": "static"
                    }
                ],
                "max_attempts": 3
            }
        ],
        "categories": [
            {
                "name": "Web",
                "description": "Web application security challenges",
                "color": "#e74c3c"
            },
            {
                "name": "Crypto",
                "description": "Cryptography and encryption challenges", 
                "color": "#9b59b6"
            },
            {
                "name": "Pwn",
                "description": "Binary exploitation challenges",
                "color": "#e67e22"
            },
            {
                "name": "Reverse",
                "description": "Reverse engineering challenges",
                "color": "#f39c12"
            },
            {
                "name": "Forensics",
                "description": "Digital forensics and analysis challenges",
                "color": "#2ecc71"
            },
            {
                "name": "Misc",
                "description": "Miscellaneous and general knowledge challenges",
                "color": "#34495e"
            }
        ],
        "instructions": {
            "format": "This is a sample challenge template for importing challenges into DCTFd",
            "supported_formats": ["JSON"],
            "challenge_fields": {
                "required": ["name", "description", "category", "difficulty", "value"],
                "optional": ["hints", "max_attempts", "type", "state", "is_visible", "author", "flag_logic"]
            },
            "flag_types": ["static", "regex", "dynamic"],
            "difficulty_range": "1-5 (1=Easy, 5=Hard)",
            "notes": [
                "Categories will be created automatically if they don't exist",
                "Flags support both static text and regex patterns",
                "Hints are optional and can have associated costs",
                "Connection info is useful for web/network challenges"
            ]
        }
    }
    
    json_content = json.dumps(template_data, indent=2, ensure_ascii=False)
    
    response = HttpResponse(json_content, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="challenge_template.json"'
    return response


@login_required
@organizer_required
def challenges_import_results(request):
    """Display challenge import results"""
    import_results = request.session.get('import_results', {})
    
    # Clear the session data
    if 'import_results' in request.session:
        del request.session['import_results']
    
    # If no import results, redirect to challenges page
    if not import_results:
        messages.error(request, _("No import results found."))
        return redirect("organizer:challenges")
    
    context = {
        'import_results': import_results,
        'title': _("Challenge Import Results"),
    }
    
    return render(request, "organizer/challenges/import_results.html", context)


@login_required
@organizer_required
def challenge_detail(request, challenge_id):
    """View challenge details"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Get submissions for this challenge
    submissions = (
        Submission.objects.filter(challenge=challenge)
        .select_related("user", "team")
        .order_by("-submitted_at")
    )

    context = {
        "challenge": challenge,
        "submissions": submissions,
    }

    return render(request, "organizer/challenges/detail.html", context)


@login_required
@organizer_required
def challenge_export(request, challenge_id):
    """Export a challenge to JSON format"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Create a JSON-serializable representation of the challenge
    challenge_data = {
        "name": challenge.name,
        "description": challenge.description,
        "category": challenge.category.name if challenge.category else "Uncategorized",
        "difficulty": challenge.difficulty,
        "points": challenge.points,
        "flag": challenge.flag,
        "created_at": (
            challenge.created_at.isoformat() if challenge.created_at else None
        ),
    }

    # Return the challenge data as a downloadable JSON file
    response = JsonResponse(
        {"challenge": challenge_data}, json_dumps_params={"indent": 4}
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{challenge.name.replace(" ", "_")}.json"'
    )
    return response


@login_required
@organizer_required
def challenge_duplicate(request, challenge_id):
    """Duplicate an existing challenge"""
    original_challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Create a new challenge with the same properties
    new_challenge = Challenge.objects.create(
        name=f"Copy of {original_challenge.name}",
        description=original_challenge.description,
        category=original_challenge.category,
        difficulty=original_challenge.difficulty,
        points=original_challenge.points,
        flag=original_challenge.flag,
        created_by=request.user,
    )

    messages.success(
        request,
        _(f'Challenge "{original_challenge.name}" was duplicated successfully.'),
    )
    return redirect("organizer:edit_challenge", challenge_id=new_challenge.id)


@login_required
@organizer_required
def challenge_file_add(request, challenge_id):
    """Add a file attachment to a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]

        # Example placeholder - in a real app, you'd save the file and create
        # a ChallengeFile model instance or similar
        # file_obj = ChallengeFile.objects.create(
        #     challenge=challenge,
        #     file=file,
        #     name=file.name
        # )

        messages.success(request, _(f'File "{file.name}" added to challenge.'))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def challenge_file_delete(request, challenge_id, file_id):
    """Delete a file attachment from a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Example placeholder - in a real app, you'd retrieve and delete the file
    # file_obj = get_object_or_404(ChallengeFile, pk=file_id, challenge=challenge)
    # file_name = file_obj.name
    # file_obj.delete()

    if request.method == "POST":
        messages.success(request, _("File deleted from challenge."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def challenge_submissions(request, challenge_id):
    """View all submissions for a specific challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    # Get all submissions for this challenge
    submissions = (
        Submission.objects.filter(challenge=challenge)
        .select_related("user", "team")
        .order_by("-submitted_at")
    )

    context = {"challenge": challenge, "submissions": submissions}

    return render(request, "organizer/challenges/submissions.html", context)


@login_required
@organizer_required
def flag_add(request, challenge_id):
    """Add a flag to a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        flag_type = request.POST.get("type", "static")
        flag_value = request.POST.get("value", "")

        if flag_value:
            # In a real app, you might have a Flag model
            # Flag.objects.create(
            #     challenge=challenge,
            #     type=flag_type,
            #     value=flag_value
            # )

            # For now, just update the challenge's flag field
            challenge.flag = flag_value
            challenge.save()

            messages.success(request, _("Flag added successfully."))
        else:
            messages.error(request, _("Flag value is required."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def flag_edit(request, challenge_id, flag_id):
    """Edit a flag for a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        flag_value = request.POST.get("value", "")

        if flag_value:
            # In a real app with a Flag model:
            # flag = get_object_or_404(Flag, pk=flag_id, challenge=challenge)
            # flag.value = flag_value
            # flag.save()

            # For now, just update the challenge's flag field
            challenge.flag = flag_value
            challenge.save()

            messages.success(request, _("Flag updated successfully."))
        else:
            messages.error(request, _("Flag value is required."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def flag_delete(request, challenge_id, flag_id):
    """Delete a flag from a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        # In a real app with a Flag model:
        # flag = get_object_or_404(Flag, pk=flag_id, challenge=challenge)
        # flag.delete()

        # For now, just clear the challenge's flag field
        challenge.flag = ""
        challenge.save()

        messages.success(request, _("Flag deleted successfully."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


# Hint management views
@login_required
@organizer_required
def hint_add(request, challenge_id):
    """Add a hint to a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)

    if request.method == "POST":
        content = request.POST.get("content", "")
        cost = request.POST.get("cost", "0")

        if content:
            try:
                cost = int(cost)
                hint = Hint.objects.create(
                    challenge=challenge, content=content, cost=cost
                )

                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {
                            "success": True,
                            "hint_id": hint.id,
                            "content": hint.content,
                            "cost": hint.cost,
                        }
                    )

                messages.success(request, _("Hint added successfully."))
            except ValueError:
                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {"success": False, "error": "Invalid cost value"}
                    )
                messages.error(request, _("Invalid cost value."))
        else:
            if request.headers.get("Accept") == "application/json":
                return JsonResponse(
                    {"success": False, "error": "Hint content is required"}
                )
            messages.error(request, _("Hint content is required."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def hint_edit(request, challenge_id, hint_id):
    """Edit a hint for a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    hint = get_object_or_404(Hint, pk=hint_id, challenge=challenge)

    if request.method == "POST":
        content = request.POST.get("content", "")
        cost = request.POST.get("cost", "0")

        if content:
            try:
                cost = int(cost)
                hint.content = content
                hint.cost = cost
                hint.save()

                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {
                            "success": True,
                            "hint_id": hint.id,
                            "content": hint.content,
                            "cost": hint.cost,
                        }
                    )

                messages.success(request, _("Hint updated successfully."))
            except ValueError:
                if request.headers.get("Accept") == "application/json":
                    return JsonResponse(
                        {"success": False, "error": "Invalid cost value"}
                    )
                messages.error(request, _("Invalid cost value."))
        else:
            if request.headers.get("Accept") == "application/json":
                return JsonResponse(
                    {"success": False, "error": "Hint content is required"}
                )
            messages.error(request, _("Hint content is required."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def hint_delete(request, challenge_id, hint_id):
    """Delete a hint from a challenge"""
    challenge = get_object_or_404(Challenge, pk=challenge_id)
    hint = get_object_or_404(Hint, pk=hint_id, challenge=challenge)

    if request.method == "POST":
        hint.delete()

        if request.headers.get("Accept") == "application/json":
            return JsonResponse({"success": True})

        messages.success(request, _("Hint deleted successfully."))

    return redirect("organizer:challenge_detail", challenge_id=challenge.id)


@login_required
@organizer_required
def team_detail(request, team_id):
    """View team details"""
    team = get_object_or_404(Team, pk=team_id)

    # Get team members
    members = team.members.all()

    # Get team submissions
    submissions = (
        Submission.objects.filter(team=team)
        .select_related("challenge")
        .order_by("-submitted_at")
    )

    # Get solved challenges
    solved_challenges = Challenge.objects.filter(
        submissions__team=team, submissions__is_correct=True
    ).distinct()

    context = {
        "team": team,
        "members": members,
        "submissions": submissions,
        "solved_challenges": solved_challenges,
    }

    return render(request, "organizer/teams/detail.html", context)


@login_required
@organizer_required
def export_scoreboard(request, format="csv"):
    """Export scoreboard in various formats"""
    teams = Team.objects.all().order_by("-score")

    if format == "json":
        # Export as JSON
        data = [
            {
                "rank": idx + 1,
                "name": team.name,
                "score": team.score,
                "last_submission": (
                    team.last_submission.isoformat() if team.last_submission else None
                ),
                "member_count": team.members.count(),
            }
            for idx, team in enumerate(teams)
        ]

        response = JsonResponse(data, safe=False, json_dumps_params={"indent": 4})
        response["Content-Disposition"] = 'attachment; filename="scoreboard.json"'
        return response
    else:
        # Default to CSV export
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="scoreboard.csv"'

        writer = csv.writer(response)
        writer.writerow(["Rank", "Team", "Score", "Last Submission"])

        for idx, team in enumerate(teams):
            writer.writerow(
                [
                    idx + 1,
                    team.name,
                    team.score,
                    team.last_submission if team.last_submission else "N/A",
                ]
            )

        return response


@login_required
@organizer_required
def ctf_controls(request):
    """CTF Controls page for moderators"""
    event = Event.objects.first()  # In a single event setup

    # Get statistics
    total_users = User.objects.count()
    total_teams = Team.objects.count()
    total_challenges = Challenge.objects.count()
    total_solves = Submission.objects.filter(is_correct=True).count()
    total_submissions = Submission.objects.count()

    # Get recent announcements
    try:
        from core.models import Announcement

        recent_announcements = Announcement.objects.order_by("-created_at")[:5]
    except:
        recent_announcements = []

    context = {
        "event": event,
        "total_users": total_users,
        "total_teams": total_teams,
        "total_challenges": total_challenges,
        "total_solves": total_solves,
        "total_submissions": total_submissions,
        "recent_announcements": recent_announcements,
    }

    return render(request, "organizer/ctf_controls.html", context)


@login_required
@organizer_required
def pause_ctf(request):
    """Pause the CTF competition"""
    if request.method == "POST":
        event = Event.objects.first()  # In a single event setup
        if event:
            event.status = "paused"
            event.save()
            messages.success(request, _("CTF has been paused."))

    return redirect("organizer:ctf_controls")


@login_required
@organizer_required
def resume_ctf(request):
    """Resume the CTF competition"""
    if request.method == "POST":
        event = Event.objects.first()  # In a single event setup
        if event:
            event.status = "running"
            event.save()
            messages.success(request, _("CTF has been resumed."))

    return redirect("organizer:ctf_controls")


@login_required
@organizer_required
def start_ctf(request):
    """Start the CTF competition"""
    if request.method == "POST":
        event = Event.objects.first()  # In a single event setup
        if event:
            event.status = "running"
            event.start_time = timezone.now()
            event.save()
            messages.success(request, _("CTF has been started."))

    return redirect("organizer:ctf_controls")


@login_required
@organizer_required
def end_ctf(request):
    """End the CTF competition"""
    if request.method == "POST":
        event = Event.objects.first()  # In a single event setup
        if event:
            event.status = "finished"
            event.end_time = timezone.now()
            event.save()
            messages.success(request, _("CTF has been ended."))

    return redirect("organizer:ctf_controls")


@login_required
@organizer_required
def send_announcement(request):
    """Send an announcement to all CTF participants"""
    if request.method == "POST":
        announcement_text = request.POST.get("announcement", "").strip()
        is_important = request.POST.get("important", False) == "on"

        if announcement_text:
            # Create an announcement
            from core.models import Announcement

            announcement = Announcement.objects.create(
                content=announcement_text, is_important=is_important, active=True
            )

            # In the future, you might want to notify users in real-time
            # (e.g., through WebSockets)

            messages.success(
                request, _("Announcement has been sent to all participants.")
            )
        else:
            messages.error(request, _("Announcement text cannot be empty."))

    return redirect("organizer:ctf_controls")


@login_required
@organizer_required
@login_required
@organizer_required
def setup_ctf(request):
    """Setup a new CTF"""
    event = Event.objects.first()  # In a single event setup

    # If event already exists, redirect to settings
    if event and event.name:
        return redirect("organizer:settings")

    # Otherwise show the setup form
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            # Create or update the event
            if event:
                for key, value in form.cleaned_data.items():
                    setattr(event, key, value)
                event.save()
            else:
                event = form.save()

            messages.success(request, _("CTF event has been set up successfully!"))
            return redirect("organizer:dashboard")
    else:
        # Pre-populate form with default values if event exists
        initial_data = {}
        if event:
            for field in EventForm.Meta.fields:
                initial_data[field] = getattr(event, field, None)

        form = EventForm(initial=initial_data)

    return render(request, "organizer/setup_ctf.html", {"form": form})


@login_required
@organizer_required
def reset_ctf(request):
    """Reset the CTF (clear submissions)"""
    if request.method == "POST":
        # Delete all submissions
        Submission.objects.all().delete()

        # Reset team scores
        Team.objects.all().update(score=0, last_submission=None)

        messages.success(
            request, _("CTF has been reset. All submissions have been cleared.")
        )

    return redirect("organizer:settings")


@login_required
@organizer_required
def delete_ctf(request):
    """Delete the CTF (all data)"""
    if request.method == "POST":
        # Delete all related data
        Submission.objects.all().delete()
        Challenge.objects.all().delete()
        ChallengeCategory.objects.all().delete()

        # Reset event
        event = Event.objects.first()
        if event:
            event.name = "New CTF"
            event.description = ""
            event.start_time = None
            event.end_time = None
            event.status = "setup"
            event.save()

        messages.success(request, _("CTF has been deleted. All data has been cleared."))

    return redirect("organizer:settings")


@login_required
@organizer_required
def categories(request):
    """List all challenge categories"""
    # Show all categories including hidden ones for organizers
    categories = ChallengeCategory.objects.all().order_by("order", "name")
    form = ChallengeCategoryForm()  # Add form for new category creation

    return render(
        request,
        "organizer/challenges/categories.html",
        {"categories": categories, "form": form},
    )


@login_required
@organizer_required
def add_category(request):
    """Add a new challenge category"""
    if request.method == "POST":
        form = ChallengeCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, _("Category added successfully."))

            # If it's an AJAX request, return JSON response
            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest" or "application/json" in request.headers.get(
                "Accept", ""
            ):
                return JsonResponse(
                    {
                        "success": True,
                        "category_id": category.id,
                        "category_name": category.name,
                    }
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

            # If it's an AJAX request, return error
            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest" or "application/json" in request.headers.get(
                "Accept", ""
            ):
                return JsonResponse({"success": False, "message": "Validation error"})

        return redirect("organizer:categories")

    # If GET, redirect to the categories page with the form
    return redirect("organizer:categories")


@login_required
@organizer_required
def edit_category(request, category_id):
    """Edit an existing challenge category"""
    category = get_object_or_404(ChallengeCategory, id=category_id)

    if request.method == "POST":
        form = ChallengeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("Category updated successfully."))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return redirect("organizer:categories")

    # If GET, show the edit form
    form = ChallengeCategoryForm(instance=category)
    return render(
        request,
        "organizer/challenges/edit_category.html",
        {"form": form, "category": category},
    )


@login_required
@organizer_required
def delete_category(request, category_id):
    """Delete a challenge category"""
    category = get_object_or_404(ChallengeCategory, id=category_id)

    if request.method == "POST":
        try:
            # Check if category has challenges
            challenge_count = Challenge.objects.filter(category=category).count()

            if challenge_count > 0:
                hide_category = request.POST.get("hide_instead", False) == "true"

                if hide_category:
                    # Set the is_hidden flag to true
                    category.is_hidden = True
                    category.save()
                    messages.success(request, _("Category hidden successfully."))
                else:
                    messages.warning(
                        request,
                        _(
                            "This category has associated challenges. Reassign them before deleting or choose to hide instead."
                        ),
                    )
                    return render(
                        request,
                        "organizer/challenges/delete_category.html",
                        {"category": category, "challenge_count": challenge_count},
                    )
            else:
                category.delete()
                messages.success(request, _("Category deleted successfully."))
        except Exception as e:
            messages.error(request, str(e))

        return redirect("organizer:categories")

    # Show confirmation page with option to hide instead of delete
    challenge_count = Challenge.objects.filter(category=category).count()
    return render(
        request,
        "organizer/challenges/delete_category.html",
        {"category": category, "challenge_count": challenge_count},
    )


@login_required
@organizer_required
def toggle_category_visibility(request, category_id):
    """Toggle the visibility of a challenge category"""
    if request.method == "POST":
        category = get_object_or_404(ChallengeCategory, id=category_id)
        category.is_hidden = not category.is_hidden
        category.save()

        status = "hidden" if category.is_hidden else "visible"
        messages.success(request, _(f'Category "{category.name}" is now {status}.'))

    return redirect("organizer:categories")
