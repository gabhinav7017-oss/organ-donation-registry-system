from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from .models import Donor, Recipient, OrganMatch, BLOOD_COMPATIBILITY, BLOOD_TYPE_CHOICES, ORGAN_CHOICES, MATCH_STATUS_CHOICES
from .forms import DonorForm, RecipientForm, OrganMatchForm


# ──────────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────────

def dashboard(request):
    total_donors = Donor.objects.count()
    active_donors = Donor.objects.filter(status='Active').count()
    total_recipients = Recipient.objects.count()
    active_recipients = Recipient.objects.filter(status='Active').count()
    total_matches = OrganMatch.objects.count()
    pending_matches = OrganMatch.objects.filter(status='Pending').count()
    completed_matches = OrganMatch.objects.filter(status='Completed').count()
    recent_donors = Donor.objects.all()[:5]
    recent_recipients = Recipient.objects.all()[:5]
    recent_matches = OrganMatch.objects.select_related('donor', 'recipient').all()[:5]

    urgency_stats = {
        'Critical': Recipient.objects.filter(urgency='Critical', status='Active').count(),
        'High': Recipient.objects.filter(urgency='High', status='Active').count(),
        'Medium': Recipient.objects.filter(urgency='Medium', status='Active').count(),
        'Low': Recipient.objects.filter(urgency='Low', status='Active').count(),
    }

    context = {
        'total_donors': total_donors,
        'active_donors': active_donors,
        'total_recipients': total_recipients,
        'active_recipients': active_recipients,
        'total_matches': total_matches,
        'pending_matches': pending_matches,
        'completed_matches': completed_matches,
        'recent_donors': recent_donors,
        'recent_recipients': recent_recipients,
        'recent_matches': recent_matches,
        'urgency_stats': urgency_stats,
    }
    return render(request, 'registry/dashboard.html', context)


# ──────────────────────────────────────────────
#  Donor Views
# ──────────────────────────────────────────────

def donor_list(request):
    query = request.GET.get('q', '')
    blood_type = request.GET.get('blood_type', '')
    status = request.GET.get('status', '')
    donors = Donor.objects.all()
    if query:
        donors = donors.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    if blood_type:
        donors = donors.filter(blood_type=blood_type)
    if status:
        donors = donors.filter(status=status)
    return render(request, 'registry/donor_list.html', {
        'donors': donors,
        'query': query,
        'blood_type': blood_type,
        'status': status,
        'blood_type_choices': BLOOD_TYPE_CHOICES,
    })


def donor_detail(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    matches = OrganMatch.objects.filter(donor=donor).select_related('recipient')
    return render(request, 'registry/donor_detail.html', {'donor': donor, 'matches': matches})


def donor_create(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor registered successfully.')
            return redirect('donor_list')
    else:
        form = DonorForm()
    return render(request, 'registry/donor_form.html', {'form': form, 'title': 'Register Donor'})


def donor_edit(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donor updated successfully.')
            return redirect('donor_detail', pk=pk)
    else:
        form = DonorForm(instance=donor)
    return render(request, 'registry/donor_form.html', {'form': form, 'title': 'Edit Donor', 'donor': donor})


def donor_delete(request, pk):
    donor = get_object_or_404(Donor, pk=pk)
    if request.method == 'POST':
        donor.delete()
        messages.success(request, 'Donor record deleted.')
        return redirect('donor_list')
    return render(request, 'registry/confirm_delete.html', {'object': donor, 'type': 'Donor'})


# ──────────────────────────────────────────────
#  Recipient Views
# ──────────────────────────────────────────────

def recipient_list(request):
    query = request.GET.get('q', '')
    blood_type = request.GET.get('blood_type', '')
    organ = request.GET.get('organ', '')
    urgency = request.GET.get('urgency', '')
    recipients = Recipient.objects.all()
    if query:
        recipients = recipients.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        )
    if blood_type:
        recipients = recipients.filter(blood_type=blood_type)
    if organ:
        recipients = recipients.filter(organ_needed=organ)
    if urgency:
        recipients = recipients.filter(urgency=urgency)
    return render(request, 'registry/recipient_list.html', {
        'recipients': recipients,
        'query': query,
        'blood_type': blood_type,
        'organ': organ,
        'urgency': urgency,
        'blood_type_choices': BLOOD_TYPE_CHOICES,
        'organ_choices': ORGAN_CHOICES,
    })


def recipient_detail(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    matches = OrganMatch.objects.filter(recipient=recipient).select_related('donor')
    return render(request, 'registry/recipient_detail.html', {'recipient': recipient, 'matches': matches})


def recipient_create(request):
    if request.method == 'POST':
        form = RecipientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipient registered successfully.')
            return redirect('recipient_list')
    else:
        form = RecipientForm()
    return render(request, 'registry/recipient_form.html', {'form': form, 'title': 'Register Recipient'})


def recipient_edit(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        form = RecipientForm(request.POST, instance=recipient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recipient updated successfully.')
            return redirect('recipient_detail', pk=pk)
    else:
        form = RecipientForm(instance=recipient)
    return render(request, 'registry/recipient_form.html', {
        'form': form, 'title': 'Edit Recipient', 'recipient': recipient,
    })


def recipient_delete(request, pk):
    recipient = get_object_or_404(Recipient, pk=pk)
    if request.method == 'POST':
        recipient.delete()
        messages.success(request, 'Recipient record deleted.')
        return redirect('recipient_list')
    return render(request, 'registry/confirm_delete.html', {'object': recipient, 'type': 'Recipient'})


# ──────────────────────────────────────────────
#  Organ Matching Views
# ──────────────────────────────────────────────

def match_list(request):
    status_filter = request.GET.get('status', '')
    matches = OrganMatch.objects.select_related('donor', 'recipient').all()
    if status_filter:
        matches = matches.filter(status=status_filter)
    return render(request, 'registry/match_list.html', {
        'matches': matches,
        'status_filter': status_filter,
        'status_choices': MATCH_STATUS_CHOICES,
    })


def match_detail(request, pk):
    match = get_object_or_404(OrganMatch.objects.select_related('donor', 'recipient'), pk=pk)
    return render(request, 'registry/match_detail.html', {'match': match})


def match_create(request):
    if request.method == 'POST':
        form = OrganMatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match recorded successfully.')
            return redirect('match_list')
    else:
        form = OrganMatchForm()
    return render(request, 'registry/match_form.html', {'form': form, 'title': 'Create Match'})


def match_edit(request, pk):
    match = get_object_or_404(OrganMatch, pk=pk)
    if request.method == 'POST':
        form = OrganMatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match updated.')
            return redirect('match_detail', pk=pk)
    else:
        form = OrganMatchForm(instance=match)
    return render(request, 'registry/match_form.html', {'form': form, 'title': 'Edit Match', 'match': match})


def match_delete(request, pk):
    match = get_object_or_404(OrganMatch, pk=pk)
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Match deleted.')
        return redirect('match_list')
    return render(request, 'registry/confirm_delete.html', {'object': match, 'type': 'Match'})


def auto_match(request):
    """Auto-match active recipients with compatible active donors."""
    recipients = Recipient.objects.filter(status='Active')
    suggestions = []
    for recipient in recipients:
        compatible_blood_types = [
            donor_type for donor_type, compatible in BLOOD_COMPATIBILITY.items()
            if recipient.blood_type in compatible
        ]
        compatible_donors = Donor.objects.filter(
            status='Active',
            blood_type__in=compatible_blood_types,
        )
        for donor in compatible_donors:
            if recipient.organ_needed in donor.organs:
                already_matched = OrganMatch.objects.filter(
                    donor=donor,
                    recipient=recipient,
                    organ=recipient.organ_needed,
                ).exists()
                if not already_matched:
                    suggestions.append({
                        'donor': donor,
                        'recipient': recipient,
                        'organ': recipient.organ_needed,
                    })

    if request.method == 'POST':
        donor_id = request.POST.get('donor_id')
        recipient_id = request.POST.get('recipient_id')
        organ = request.POST.get('organ')
        if donor_id and recipient_id and organ:
            donor = get_object_or_404(Donor, pk=donor_id)
            recipient = get_object_or_404(Recipient, pk=recipient_id)
            match, created = OrganMatch.objects.get_or_create(
                donor=donor, recipient=recipient, organ=organ,
                defaults={'status': 'Pending'},
            )
            if created:
                messages.success(request, f'Match created: {organ} — {donor.full_name} → {recipient.full_name}')
            else:
                messages.info(request, 'This match already exists.')
        return redirect('auto_match')

    return render(request, 'registry/auto_match.html', {'suggestions': suggestions})
