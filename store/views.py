# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template import loader

from .models import App,Category,HeuristicScore,Participant

from appstore.settings import BASE_DIR

from collections import OrderedDict
import csv
import datetime
import json
import operator
import os
import random

h_cats = OrderedDict([(7,"notice"),(15,"consent"),(19,"access"),(26,"social")])

questions = ["I should be told who is collecting data about me before it happens.",
        "I should be told what happens to my data before it is collected.",
        "I should be told who my data will be shared with before it is collected.",
        "I should be told how data about me is collected.",
        "I should be told what steps are taken to maintain the confidentiality and integrity of my data.",
        "I want to be able to read Terms of Service or a Privacy Policy before using a new service.",
        "I should be able to decide whether my data are used for additional purposes, such as marketing or research.",
        "I should have to give consent before my data are collected.",
        "Consent forms shouldn't have a confusing mix of boxes to tick and untick.",
        "I should be able to choose exactly which types of data get collected. For example, letting a running app track my steps but not my heart rate.",
        "If a service wants to collect new types of data, I should have to consent to it first.",
        "If a service wants to use my data for new reasons, I should have to give consent for this again.",
        "If a service wants to share my data with new third parties, I should have to give consent for this again.",
        "I should be able to revoke consent to my data being used for any purpose, at any time.",
        "I should have control over where my data are stored, such as on my phone, or with a third party service.",
        "I should be able to export my data from a service.",
        "When I export data from a service it should be available in standard text formats, such as CSV.",
        "I should be able to export my data from a service without having to contact customer support.",
        "I should be able to let other services access my data, for example if I want to combine health data from multiple apps, or write scripts to access my data.",
        "I should be able to choose which activities get shared with sites such as Facebook, rather than it happening automatically.",
        "I should be able to choose exactly what information gets shared with sites such as Facebook. For example, I might want to share that I lost weight, but not how much.",
        "I want to explicitly confirm if I am happy for something to be shared with sites such as Facebook, and to easily be able to delete it if I change my mind.",
        "When I'm deciding to share something with sites such as Facebook, I want to clearly see what I'm sharing and who will be able to see it.",
        "I don't want to be distracted by irrelevant information when I'm deciding what information to share with sites such as Facebook, or with whom I want to share it.",
        "When I share something with sites such as Facebook, I expect the shared activity to match the way it was shown to me in the app first.",
        "When I share something with sites such as Facebook, I expect to be able to get help to choose the right privacy settings."
]

task_list = ["You want to track how far you travel on your bike",
            "You want to better understand what's in the food you eat",
            "You want to track your performance in the gym",
            "You want to check your resting heart rate isn't too high",
            "You want to keep track of what time of day you feel less happy",
            "You want to track the progress of your marathon training",
            "You want to see when you're feeling more restless during the night",
            "You want to keep better track of your finances",
            "You want to make sure you're walking enough every day",
            "You want to be more disciplined about how long you spend working on a task",
            "You want to see how close you are to your ideal weight"
]

task_to_cat = ['Cycling','Diet','Exercise','Heart','Mood','Running','Sleep','Spending','Steps','Time','Weight']

def store_context(request):
    """
        Context processor which injects a list of app categories and the current task
        into all responses for common template tasks
    """
    if "task" in request.session:
        task = task_list[int(request.session["task"])].split(" ")[3:]
        task = " ".join(task)
    else:
        task = "NO TASK BAD BAD BAD"

    cats = get_cats()

    return {'task':task,'cats':cats}



"""
    Landing page for study, leading to information sheet and consent
"""
def index(request):
    if request.session.get('done',0) == 1:
        return render(request, "store/done.html", {})
    return render(request, "store/info.html", {})

"""
    Participant information
"""
def info(request):
    return render(request, "store/info.html", {})

"""
    Participant consent
"""
def consent(request):
    return render(request, "store/consent.html", {})

"""
    Clears this user's session
"""
def clear(request):
    request.session.clear()
    return HttpResponse("cleared")
"""
    Store response then return next question for profiler questionnaire
"""
def next_profile(request):
    answer = request.GET.get("response")
    other = request.GET.get("reject")
    ranks = request.session.get("ranks",{})

    if len(ranks) == 0:
        #initialise ranks dict
        for i in xrange(0,26):
            ranks[str(i)] = 0

    ranks[answer] += 1
    #ranks[other] -= 1
    request.session["ranks"] = ranks

    ###
    ### STRATEGY: repeat until all heuristic groups disambiguated

    # aggregate the four groups
    # totals = {'notice':0,'consent':0,'access':0,'social':0}
    # for rank in ranks:
    #     for cat in h_cats:
    #         if int(rank) < cat:
    #             this_cat = h_cats[cat]
    #             totals[this_cat] += ranks[rank]
    #             break
    #
    # print ranks
    # print totals
    #
    # seen = []
    # ask_again = False
    # for cat in totals:
    #     if(totals[cat] in seen):
    #         ask_again = True
    #         break
    #     seen.append(totals[cat])
    #
    # zeros = 0
    # for rank in ranks:
    #     if ranks[rank] == 0:
    #         zeros+=1



    ###
    ### STRATEGY: repeat until all terms disambiguated
    ###

    seen = []
    zeros = 0
    have_dupes = False

    print ranks

    for rank in ranks:
        if ranks[rank] in seen:
            have_dupes = True
            zeros +=1
            src_idx, other_idx = None, None
            #break
        else:
            seen.append(ranks[rank])
    if have_dupes:
        while True:
            poss_dupes = []
            # keep trying to find a dupe pair
            src_idx = random.randint(0,25)
            for rank in ranks:
                if ranks[str(rank)] == ranks[str(src_idx)] and int(rank) != src_idx:
                    poss_dupes.append(rank)
            if len(poss_dupes) > 0:
                other_idx = int(random.choice(poss_dupes))
                break

    if len(seen) < 26:
        ask_again = True

    ###
    ### STRATEGY: repeat until no zero terms
    ###

    # ask_again = False
    # zeros = 0
    # for rank in ranks:
    #     if ranks[rank] == 0:
    #         ask_again = True
    #         zeros+=1
    # if zeros == 1:
    #     ask_again = False



    # while True:
    #     app1 = random.choice(questions)
    #     app2 = random.choice(questions)
    #
    #     if app1 != app2:
    #         break

    if src_idx != None:
        app1 = questions[src_idx]
        app2 = questions[other_idx]

    zeros = 0
    ask_again = False
    for rank in ranks:
        if ranks[rank] == 0:
            ask_again = True
            zeros+=1
    if zeros == 1:
        ask_again = False

    if not ask_again:
        return JsonResponse({'status':'done'})

    perc = ((26-float(zeros))/26)*100

    apps = {'perc':perc,'0':{'id':questions.index(app1),'q':app1}, '1':{'id':questions.index(app2),'q':app2}}
    return JsonResponse(apps)


"""
    Questionnaire to profile participant
"""
def profiler(request):
    # tracks participant's progress in the profiler. returns the first set of questions
    # for each answered question, a request is made to next_profile with the answer to either
    # get the next question or mark the questionnaire as finished for redirection
    # view handles all validation logic, js is just presentation layer


    while True:
        app1 = random.choice(questions)
        app2 = random.choice(questions)

        if app1 != app2:
            break

    apps = {'0':{'id':questions.index(app1),'q':app1}, '1':{'id':questions.index(app2),'q':app2}}

    return render(request, "store/profiler.html", {"apps":apps})

"""
    Display results of profiler before linking to task
"""
def done_profiler(request):
    max_scores = {"notice":16,"consent":19,"access":9,"social":10}
    #h_cats = OrderedDict([(7,"notice"),(15,"consent"),(19,"access"),(26,"social")])

    # aggregate the ranking results
    ranks = request.session.get("ranks",{})
    if len(ranks) == 0:
        return profiler(request)
        #return error(request,"PROFILER_INCOMPLETE")
        #return HttpResponse("Please complete the questionnaire first!")

    cat_scores = {'notice':0,'consent':0,'access':0,'social':0}
    for rank in ranks:
        rank = int(rank)
        this_cat = None
        for cat in h_cats:
            if rank < cat:
                this_cat = h_cats[cat]
                break
        cat_scores[this_cat] += ranks[str(rank)]
    request.session["rank_cats"] = cat_scores

    my_ranks = request.session.get("rank_cats")
    #my_ranks = {'notice':10,'consent':5,'access':15,'social':7}
    total_score = 0
    if my_ranks:
        for cat in my_ranks:
            total_score += my_ranks[cat]

    temp_ranks = [my_ranks['social'], my_ranks['consent'], my_ranks['access'],
    my_ranks['notice']]



    return render(request, "store/profile_done.html", {'ranks':json.dumps(cat_scores),  'concerns':json.dumps(temp_ranks)})


"""
    Presents selection of tasks for participant to choose from
"""
def tasks(request):
    sorted_tasks = task_list[:]
    shuffle_tasks = task_list[:]

    random.shuffle(shuffle_tasks)
    rnd_tasks = shuffle_tasks[0:3]

    out_tasks = {}
    for task in rnd_tasks:
        out_tasks[sorted_tasks.index(task)] = task

    return render(request, "store/tasks.html", {'tasks':out_tasks})

def post_task(request):
    """
        Handle the choice of task, then client redirects to store_home
    """
    task = int(request.GET.get("task"))
    request.session["task"] = task

    participant = Participant()
    participant.task = task
    participant.condition = random.randint(0,2)
    participant.profiler_answers = request.session.get("rank_cats")
    participant.save()

    request.session["p_id"] = participant.id
    

    return HttpResponse("task stored")

def post_install(request):
    """
        Handle the choice of app to install, so client can
        redirect to debrief exercise
    """
    app = int(request.GET.get("app"))
    request.session["install"] = app
    return HttpResponse("app stored")

def get_cats():
    """ Return all categories for sidebar """

    cats = Category.objects.all()
    return cats

"""
    Index for the app store
"""
def store_home(request):

    nav = request.session.get("nav",[])
    nav.append({'page':'store_home'})
    request.session['nav'] = nav   

    count = App.objects.count()
    apps = []
    for i in xrange(0,3):
        while True:
            app = App.objects.all()[random.randint(0,count-1)]
            if app not in apps:
                apps.append(app)
                break

    #apps = App.objects.order_by('name')[:5]

    return render(request, "store/store_index.html",{'apps':apps,'do_install':True})

"""
    App search results
"""
def search(request):
    pass

def bulk_import(request):
    """
    Bulk imports all apps with basic metadata and heuristic scores
    If an app model already exists it does not exist
    """
    CSV_PATH = os.path.join(BASE_DIR, 'store/csv')
    MAIN_DATA = os.path.join(CSV_PATH, "heuristics_proc.csv")
    EXTRA_DATA = os.path.join(CSV_PATH, "extra_app_data.csv")
    REVIEW_DATA = os.path.join(CSV_PATH, "app_reviews.csv")

    with open(MAIN_DATA) as main:
        with open(EXTRA_DATA) as extra:
            with open(REVIEW_DATA) as review:
                extra_reader = csv.reader(extra)
                extra_reader.next()


                for row in extra_reader:
                    main.seek(0)
                    review.seek(0)

                    main_reader = csv.reader(main)
                    review_reader = csv.reader(review)
                    main_reader.next()
                    review_reader.next()

                    package_name = row[1]
                    description = row[2]
                    image = row[3]
                    logo = row[4]

                    app_name, category = None, None
                    # get category from reviewer csv
                    got_cat = False
                    for rev in review_reader:
                        print "is %s = %s?" % (rev[2], row[1])
                        if rev[2] == row[1]:
                            app_name = rev[3]
                            category = rev[7]
                            break

                    cat = Category.objects.get_or_create(name=category.capitalize(),
                                description=category.capitalize())

                    app = App.objects.get_or_create(package=package_name,
                    name = app_name,
                    icon_url = logo,
                    description_dom = description,
                    category = cat[0],
                    screenshot = image)

                    # get heuristic scores for this app
                    for h in main_reader:
                        if h[0] == package_name:
                            s = HeuristicScore.objects.get_or_create(app=app[0],
                            heuristic_no = h[4],
                            score = h[5])


"""
    Show apps in category by id
"""
def category(request):
    this_cat = Category.objects.get(id=request.GET.get("cat"))
    apps = App.objects.filter(category=this_cat)

    nav = request.session.get("nav",[])
    nav.append({'page':'cat','cat':this_cat.id})
    request.session['nav'] = nav   

    return render(request,"store/store_cat.html", {'do_install':True,'this_cat':this_cat,'apps':apps})


def get_scores_for_app(app):
    """
    For a given App object, returns a dict of max_scores and app_scores
    """
    this_app = app
    max_scores = {'social':10,'consent':19,'access':9,'notice':16}
    h_ranges = [2,2,2,2,2,4,2,2,2,2,2,3,3,3,2,3,2,2,2,2,1,2,1,1,1,2]
    h_cats = OrderedDict([(7,"notice"),(15,"consent"),(19,"access"),(26,"social")])


    unsafe_scores = HeuristicScore.objects.filter(app=this_app)
    scores = []
    seen_ids = []
    for score in unsafe_scores:
        if score.heuristic_no not in seen_ids:
            scores.append(score)
            seen_ids.append(score.heuristic_no)


    app_scores = {'social':0,'consent':0,'access':0,'notice':0}
    missing_h = range(0,26)

    for score in scores:
        app_scores[score.category] += score.score
        missing_h.remove(score.heuristic_no)

    for missing in missing_h:
        for c in h_cats.keys():
            if missing < c:
                cat = h_cats[c]
                break
        max_scores[cat] -= h_ranges[missing]

    score_props = {}
    for cat in max_scores:
        if(max_scores[cat] == 0):
            score_props[cat] = 0
        else:
            score_props[cat] = float(app_scores[cat]) / max_scores[cat]
    return {'app_scores':app_scores, 'max_scores':max_scores, 'score_props':score_props}

def post_brief(request):
    """
    Generates a short questionnaire depending on the app chosen by the participant
    """

    try:
        installed = App.objects.get(id=request.session.get("install"))
    except:
        return store_home(request)

    scan_data= request.session.get("rank_cats")
    scan_scores = {'social':scan_data['social'], 'consent':scan_data['consent'], 
    'access':scan_data['access'], 'notice':scan_data['notice']}

    scan_total = 0
    for scan in scan_scores:
        scan_total += scan_scores[scan]

    # normalise these scores so we know what the proportions are like
    # lets us see if an important issue has been violated by this app, etc
    scan_props = {}
    for scan in scan_scores:
        scan_props[scan] = float(scan_scores[scan])/scan_total

    # generate a set of questions based on the choice of app and the
    # participant condition

    questions = []
    # first question: FOR ALL: why did you pick this app?
    # constrain options and include free text
    questions.append({'type':'WHY_PICK'})

    # is this app in the right category?
    # allow user to justify, there may be some ambiguous cats
    # otherwise we can probably filter out this one
    t = request.session.get("task")
    if installed.category.name != task_to_cat[t]:
        # maow
        questions.append({'type':'WRONG_CAT'})
    

    # second question: if current app has bad privacy on dimensions of >.25 importance:
    # we thought this mattered to you... 
    installed_scores = get_scores_for_app(installed)
    for scan in scan_props:
        if scan_props[scan] > 0.25:
            # this is an important concern! is this app scoring > 0.5?
            if(installed_scores['score_props'][scan] < 0.5):
                if installed_scores['max_scores'][scan] > 0:
                  questions.append({'type':'THOUGHT_MATTER','dimension':scan})
            

    # third question: if an alternative was shown to user which improved on a dimension
    # with >.25 importance
    # why not this alternative app...
    alt_apps = get_alt_apps(installed)
    for scan in scan_props:
        if scan_props[scan] > 0.25:
            for app in alt_apps['better'][scan]:
                if installed_scores['max_scores'][scan] > 0:
                    questions.append({'type':'ALT_APP','cat':scan,'app_id':app.id,'app_name':app.name})

                

    # final question: for everyone: generic question about level of QS experience?
    questions.append({'type':'QS_EXP'})

    request.session['questions'] = questions

    return render(request,"store/postbrief.html",{'app':installed,'questions':json.dumps(questions),
    'scan':scan_scores,'scan_props':scan_props,'right_cat':task_to_cat[t]})

def qs_exp(request):
    """
    Ask the participant how much QS experience they have to broadly classifly
    participants as self-trackers or not, into 3 buckets:
    - self-reported: identifies as a self-quantifier
    - user: reports having used QS services (even if not currently)
    - non-user: reports never using QS services
    """

    return render(request,"store/qs_exp.html")

def submit_brief(request):
    """
    Store the responses to debrief questions
    """

    p_id = request.session.get("p_id")
    p = Participant.objects.get(id=p_id)

    p.debrief_answers = request.GET.get("responses")
    p.save()
    return HttpResponse("saved")

def save_responses(request):
    """
    Write this participant's data to the db: 
        - !task
        - !participant condition
        - !participant id
        - time taken to complete task
        - !profiler answers
        - SCAN profile
        - page navigation route
        - post-brief questions
        - !post-brief responses

    """
    p_id = request.session.get("p_id")
    p = Participant.objects.get(id=p_id)

    p.time_end = datetime.datetime.now()
    p.debrief_questions = request.session['questions']
    p.debrief_answers = request.GET.get("responses")
    p.page_nav_route = request.session['nav']
    
    p.save()

    request.session['done'] = 1
    

    return render(request,"store/thanks.html")

def error(request,msg):
    """
    Generic error handler, includes a diagnostic message and redirects user back
    to participant information
    """

    if not msg:
        msg = "UNKNOWN_ERROR"
    return render(request,"store/error.html",{'error':msg})

def get_alt_apps(this_app):
    """
        For the given app, do any perform better on any privacy dimensions?
        Returns a dict with:
            - app-set: a set of better apps for each dimension
            - story: a text story summarising how this app performs relative
            to the competition
    """
    cat_src = ['notice','consent','access','social']
    app_dict = get_scores_for_app(this_app)
    max_scores = app_dict['max_scores']
    app_scores = app_dict['app_scores']
    app_props = app_dict['score_props']

    
     # do any apps in this category score better on any dimensions?
    # group these by heuristic category and rank the best ones
    alt_apps = App.objects.filter(category=this_app.category)
    better_cats = {'notice':[],'consent':[],'access':[],'social':[]}
    worse_cats = {'notice':[],'consent':[],'access':[],'social':[]}

    max_diff_better = 0
    max_diff_better_app = None

    max_diff_worse = 0
    max_diff_worse_app = None

    app_set = {} # app: {better: {metric: diff_str}, {worse: {metric: diff_str}}}

    for app in alt_apps:
        alt_scores = get_scores_for_app(app)
        for cat in cat_src:
            if alt_scores['score_props'][cat] > app_props[cat]:
                better_cats[cat].append(app)
                if ((alt_scores['score_props'][cat] - app_props[cat]) > max_diff_better):
                    max_diff_better = alt_scores['score_props'][cat] - app_props[cat]
                    max_diff_better_app = app


    # for each better app, check if there are any poorer-performing metrics so these can be reported
    for bcat in better_cats:
        for app in better_cats[bcat]:
            alt_scores = get_scores_for_app(app)
            for incat in better_cats:
                if alt_scores['score_props'][incat] < app_props[incat]:
                    worse_cats[incat].append(app)

                    if ((app_props[incat] - alt_scores['score_props'][incat]) > max_diff_worse):
                        max_diff_worse = app_props[incat] - alt_scores['score_props'][incat]
                        max_diff_worse_app = app



    # generate a story for each one depending on how much better it is
    stories = [['BEST',"This app has no privacy issues"],
                ['GOOD', "This app has no major privacy issues"],
                ['OK', "This app may have some privacy issues"],
                ['BAD', "This app may have major privacy issues"],
                ['WORST', "This app has critical privacy issues"]]
    if max_diff_better == 0:
        story = stories[0]
    elif max_diff_worse == 0:
        story = stories[4]
    elif max_diff_worse > max_diff_better:
        story = stories[1]
    elif max_diff_worse < max_diff_better:
        story = stories[3]
    else:
        story = stories[2]

    return {'app_set':app_set,'story':story,'better':better_cats,'worse':worse_cats,
    'app_scores':app_scores,'max_scores':max_scores}




def app_listing(request):
    """
    The listing for an individual app
    """

    # t = request.session.get("task")
    # if not t:
    #     return index(request)

    do_install = True
    if(request.GET.get("ro")):
        do_install = False

    

    this_app = App.objects.get(id=request.GET.get("id"))
    cat_src = ['notice','consent','access','social']

    nav = request.session.get("nav",[])
    nav.append({'page':'app','id':this_app.id})
    request.session['nav'] = nav   

    # process this app's scores so it can be visualised meaningfully
    # box size = concern so scale boxes as a proportion of the total score
    # box color = app performance, red -> green based on proportion of max_score for each cat
    my_ranks = request.session.get("rank_cats")
    #my_ranks = {'notice':10,'consent':5,'access':15,'social':7}
    total_score = 0
    if my_ranks:
        for cat in my_ranks:
            total_score += my_ranks[cat]


    # dummy cats to test visualisation, remember to ditch this
    cat_order = ['social','consent','access','notice']

    if not my_ranks:
        return index(request)

    my_ranks = [my_ranks['social'], my_ranks['consent'], my_ranks['access'],
    my_ranks['notice']]
    #my_ranks = [random.randint(0,30),random.randint(0,30),random.randint(0,30),random.randint(0,30)]
    rank_pop = {'social':my_ranks[0],'consent':my_ranks[1],'access':my_ranks[2],'notice':my_ranks[3]}

    sorted_rank= sorted(rank_pop.items(), key=operator.itemgetter(1))
    sorted_rank = list(reversed(sorted_rank))



    # max_scores = {'social':10,'consent':19,'access':9,'notice':16}
    # h_ranges = [2,2,2,2,2,4,2,2,2,2,2,3,3,3,2,3,2,2,2,2,1,2,1,1,1,2]
    # h_cats = OrderedDict([(7,"notice"),(15,"consent"),(19,"access"),(26,"social")])
    #
    #
    # unsafe_scores = HeuristicScore.objects.filter(app=this_app)
    # scores = []
    # seen_ids = []
    # for score in unsafe_scores:
    #     if score.heuristic_no not in seen_ids:
    #         scores.append(score)
    #         seen_ids.append(score.heuristic_no)
    #
    #
    # app_scores = {'social':0,'consent':0,'access':0,'notice':0}
    # missing_h = range(0,26)
    #
    # for score in scores:
    #     app_scores[score.category] += score.score
    #     missing_h.remove(score.heuristic_no)
    #
    # for missing in missing_h:
    #     for c in h_cats.keys():
    #         if missing < c:
    #             cat = h_cats[c]
    #             break
    #     max_scores[cat] -= h_ranges[missing]
    # app_dict = get_scores_for_app(this_app)
    # max_scores = app_dict['max_scores']
    # app_scores = app_dict['app_scores']
    # app_props = app_dict['score_props']


    # # do any apps in this category score better on any dimensions?
    # # group these by heuristic category and rank the best ones
    # alt_apps = App.objects.filter(category=this_app.category)
    # better_cats = {'notice':[],'consent':[],'access':[],'social':[]}
    # worse_cats = {'notice':[],'consent':[],'access':[],'social':[]}

    # max_diff_better = 0
    # max_diff_better_app = None

    # max_diff_worse = 0
    # max_diff_worse_app = None

    # app_set = {} # app: {better: {metric: diff_str}, {worse: {metric: diff_str}}}

    # for app in alt_apps:
    #     alt_scores = get_scores_for_app(app)
    #     for cat in cat_src:
    #         if alt_scores['score_props'][cat] > app_props[cat]:
    #             better_cats[cat].append(app)
    #             if ((alt_scores['score_props'][cat] - app_props[cat]) > max_diff_better):
    #                 max_diff_better = alt_scores['score_props'][cat] - app_props[cat]
    #                 max_diff_better_app = app


    # # for each better app, check if there are any poorer-performing metrics so these can be reported
    # for bcat in better_cats:
    #     for app in better_cats[bcat]:
    #         alt_scores = get_scores_for_app(app)
    #         for incat in better_cats:
    #             if alt_scores['score_props'][incat] < app_props[incat]:
    #                 worse_cats[incat].append(app)

    #                 if ((app_props[incat] - alt_scores['score_props'][incat]) > max_diff_worse):
    #                     max_diff_worse = app_props[incat] - alt_scores['score_props'][incat]
    #                     max_diff_worse_app = app



    # # generate a story for each one depending on how much better it is
    # stories = [['BEST',"This app has no privacy issues"],
    #             ['GOOD', "This app has no major privacy issues"],
    #             ['OK', "This app may have some privacy issues"],
    #             ['BAD', "This app may have major privacy issues"],
    #             ['WORST', "This app has critical privacy issues"]]
    # if max_diff_better == 0:
    #     story = stories[0]
    # elif max_diff_worse == 0:
    #     story = stories[4]
    # elif max_diff_worse > max_diff_better:
    #     story = stories[1]
    # elif max_diff_worse < max_diff_better:
    #     story = stories[3]
    # else:
    #     story = stories[2]

    alt_dict = get_alt_apps(this_app)
    story = alt_dict['story']
    better_cats = alt_dict['better']
    worse_cats= alt_dict['worse']
    app_scores = alt_dict['app_scores']
    max_scores = alt_dict['max_scores']


    # rank the user's concerns so they are sorted in the sidebar visualisation
    # ranked_concerns = []
    # sort_concern = sorted(my_ranks)
    # for concern in sort_concern:
    #     ranked_concerns.append(better_cats.keys()[ranked_concerns.index(concern)])

    return render(request,"store/store_listing.html",{'do_install':do_install, 'cats':get_cats(),
    'app_scores':json.dumps(app_scores), 'app':this_app,'concerns':json.dumps(my_ranks),
    'max_scores':json.dumps(max_scores), 'better': better_cats, 'worse': worse_cats,
        # 'max_diff_better':max_diff_better,'max_diff_better_app':max_diff_better_app,
        # 'max_diff_worse':max_diff_worse,'max_diff_worse_app':max_diff_worse_app,
    'story':story,'sorted_rank':sorted_rank})
