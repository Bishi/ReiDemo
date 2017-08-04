import requests
import json
from datetime import datetime
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from home.forms import EditCampaignForm, EditProposalForm, EditProposalFormApproved
from django.core.urlresolvers import reverse


def home_redirect(response):
    return HttpResponseRedirect(reverse('home'))


def login_view(request):
    return render_to_response('home/login.html')


def users_view(request):
    try:
        response = requests.get('https://ct-campaign-service.herokuapp.com/person')
        content = response.content

        my_json = content.decode('utf8').replace("'", '"')
        json_data = json.loads(my_json)
    except:
        json_data = "Could not fetch Users"

    args = {}
    args.update(csrf(request))

    args['content'] = json_data

    return render_to_response('home/users.html', args)


def campaign_proposals_view(request):
    try:
        proposal_response = requests.get('https://ct-campaign-service.herokuapp.com/campaignProposal')
        content = proposal_response.content
        my_json = content.decode('utf8').replace("'", '"')
        proposal_json_data = json.loads(my_json)

        campaign_response = requests.get('https://ct-campaign-service.herokuapp.com/campaign')
        content = campaign_response.content
        my_json = content.decode('utf8').replace("'", '"')
        campaign_json_data = json.loads(my_json)

        pledge_response = requests.get('https://ct-campaign-service.herokuapp.com/campaignPledge')
        content = pledge_response.content
        my_json = content.decode('utf8').replace("'", '"')
        pledge_json_data = json.loads(my_json)

        number_of_campaigns = len(campaign_json_data)
        number_of_pledges = len(pledge_json_data)
    except:
        proposal_json_data = None
        campaign_json_data = None
        number_of_campaigns = 0
        number_of_pledges = 0
        pledge_json_data = None

    chart_data = {'Pending': 0, 'Running': 0, 'Finished': 0, 'Failed': 0}

    for campaign in campaign_json_data:
        if campaign['campaignStatus'] == 'Pending':
            chart_data['Pending'] += 1
        elif campaign['campaignStatus'] == 'Running':
            chart_data['Running'] += 1
        elif campaign['campaignStatus'] == 'Finished':
            chart_data['Finished'] += 1
        elif campaign['campaignStatus'] == 'Failed':
            chart_data['Failed'] += 1

    pledge_amount = 0
    for pledge in pledge_json_data:
        try:
            pledge_amount += pledge['pledgedAmount']
        except:
            pass

    args = {}
    args.update(csrf(request))

    args['content'] = proposal_json_data
    args['campaigns'] = number_of_campaigns
    args['pledges'] = number_of_pledges
    args['chart_data'] = chart_data
    args['pledge_amount'] = pledge_amount

    return render_to_response('home/campaign_proposals.html', args)


def campaign_proposal_details_view(request, proposal_id=None):
    try:
        response = requests.get('https://ct-campaign-service.herokuapp.com/campaignProposal/' + proposal_id)
        content = response.content

        my_json = content.decode('utf8')
        json_data = json.loads(my_json)
    except:
        raise Http404("Campaign proposal does not exist")

    args = {}
    args.update(csrf(request))

    args['proposal_id'] = proposal_id

    initial_data = {'campaign_type': json_data['campaignType'],
                    'permanent_residence': json_data['initiator']['permanentResidence'],
                    'email': json_data['initiator']['email'],
                    'mobile_number': json_data['initiator']['mobileNumber'],
                    'project_location': json_data['projectLocation'],
                    'IBAN': json_data['initiator']['iban'],
                    'campaign_page_url': json_data['campaignUrl'],
                    'campaign_page_id': json_data['campaignPageId'],
                    'description': json_data['description'],
                    'comments': json_data['approverDetails'],
                    'status': json_data['proposalStatus'],
                    }

    if request.method == 'POST':
        if json_data['proposalStatus'] == 'Approved':
            form = EditProposalFormApproved(request.POST, initial=initial_data)
        else:
            form = EditProposalForm(request.POST, initial=initial_data)

        headers = {"Content-Type": "application/json"}
        if form.is_valid():
            json_data['campaignType'] = form.cleaned_data['campaign_type']
            json_data['projectLocation'] = form.cleaned_data['project_location']
            json_data['campaignUrl'] = form.cleaned_data['campaign_page_url']
            json_data['campaignPageId'] = form.cleaned_data['campaign_page_id']
            json_data['description'] = form.cleaned_data['description']
            json_data['proposalStatus'] = form.cleaned_data['status']
            json_data['approverDetails'] = form.cleaned_data['comments']

            requests.put('https://ct-campaign-service.herokuapp.com/campaignProposal/' + proposal_id,
                         headers=headers,
                         data=json.dumps(json_data))

            if form.cleaned_data['status'] == 'Approved' and request.POST.get("start_campaign"):
                r = requests.post('https://ct-campaign-service.herokuapp.com/campaignProposal/' +
                                  proposal_id + '/start', headers=headers)
                campaign_id = json.loads(r.content.decode('utf8'))['id']
                return HttpResponseRedirect(reverse('home:campaign_details', kwargs={'campaign_id': campaign_id}))
            else:
                return HttpResponseRedirect(reverse('home:campaign_proposal_details',
                                                    kwargs={'proposal_id': proposal_id}))
    else:
        if json_data['proposalStatus'] == 'Approved':
            form = EditProposalFormApproved(initial=initial_data)
        else:
            form = EditProposalForm(initial=initial_data)

    args['form'] = form
    args['data'] = json_data

    return render_to_response('home/campaign_proposal_details.html', args)


def campaigns_view(request):
    try:
        response = requests.get('https://ct-campaign-service.herokuapp.com/campaign')
        content = response.content

        my_json = content.decode('utf8')
        json_data = json.loads(my_json)

        for entry in json_data:
            if entry['currentAmount'] is not None and entry['targetAmount'] is not None:
                current = (entry['currentAmount'])
                target = (entry['targetAmount'])
                value = ((current / target) * 100)
                entry['progress'] = round(value, 2)
    except:
        json_data = "Could not fetch Campaigns"

    args = {}
    args.update(csrf(request))

    args['content'] = json_data

    return render_to_response('home/campaigns.html', args)


def campaign_details_view(request, campaign_id=None):
    try:
        response = requests.get('https://ct-campaign-service.herokuapp.com/campaign/' + campaign_id)
        content = response.content

        my_json = content.decode('utf8').replace("'", '"')
        json_data = json.loads(my_json)
    except:
        raise Http404("Campaign  does not exist")

    args = {}
    args.update(csrf(request))

    args['campaign_id'] = campaign_id

    initial_data = {'campaign_type': "test",
                    'permanent_residence': json_data['owner']['permanentResidence'],
                    'email': json_data['owner']['email'],
                    'mobile_number': json_data['owner']['mobileNumber'],
                    'IBAN': json_data['owner']['iban'],
                    'campaign_page_url': json_data['campaignUrl'],
                    'description': json_data['description'],
                    'comments': json_data['comment'],
                    'status': json_data['campaignStatus'],
                    }

    date_format = "%Y-%m-%d"
    today_date = datetime.today()
    end_date = datetime.strptime(json_data['endDate'], date_format)
    if end_date > today_date:
        remaining = abs((today_date - end_date).days)
    else:
        remaining = 0

    if request.method == 'POST':
        form = EditCampaignForm(request.POST, initial=initial_data)
        if form.is_valid():
            return HttpResponseRedirect(reverse('home:campaigns'))
    else:
        form = EditCampaignForm(initial=initial_data)

    args['form'] = form
    args['data'] = json_data
    args['remaining'] = remaining

    return render_to_response('home/campaign_details.html', args)


def transactions_view(request):
    try:
        response = requests.get('https://ct-campaign-service.herokuapp.com/campaignPledge/')
        content = response.content

        my_json = content.decode('utf8')
        json_data = json.loads(my_json)
    except:
        raise Http404("Cannot fetch transactions")

    args = {}
    args.update(csrf(request))

    args['content'] = json_data

    return render_to_response('home/transactions.html', args)
