from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Review, Restaurant, Cluster
from .forms import ReviewForm
from .suggestions import update_clusters

import datetime

from django.contrib.auth.decorators import login_required

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'reviews/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})


def restaurant_list(request):
    restaurant_list = Restaurant.objects.order_by('-name')
    context = {'restaurant_list':restaurant_list}
    return render(request, 'reviews/restaurant_list.html', context)


def restaurant_detail(request, res_id):
    restaurant = get_object_or_404(Restaurant, pk=res_id)
    form = ReviewForm()
    return render(request, 'reviews/restaurant_detail.html', {'restaurant': restaurant, 'form': form})

@login_required
def add_review(request, res_id):
    restaurant = get_object_or_404(Restaurant, pk=res_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        user_name = request.user.username
        review = Review()
        review.restaurant = restaurant
        review.user_name = user_name
        review.rating = rating
        review.comment = comment
        review.pub_date = datetime.datetime.now()
        review.save()
        update_clusters()
     
        return HttpResponseRedirect(reverse('reviews:restaurant_detail', args=(restaurant.id,)))
    
    return render(request, 'reviews/restaurant_detail.html', {'restaurant': restaurant, 'form': form})
    

def user_review_list(request, username=None):
    if not username:
        username = request.user.username
    latest_review_list = Review.objects.filter(user_name=username).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':username}
    return render(request, 'reviews/user_review_list.html', context)


@login_required
def user_recommendation_list(request):
    
    
    user_reviews = Review.objects.filter(user_name=request.user.username).prefetch_related('restaurant')
    user_reviews_restaurant_ids = set(map(lambda x: x.restaurant.id, user_reviews))


    try:
        user_cluster_name = \
            User.objects.get(username=request.user.username).cluster_set.first().name
    except: # if no cluster assigned for a user, update clusters
        update_clusters()
        user_cluster_name = \
            User.objects.get(username=request.user.username).cluster_set.first().name
    
    
    user_cluster_other_members = \
        Cluster.objects.get(name=user_cluster_name).users \
            .exclude(username=request.user.username).all()
    other_members_usernames = set(map(lambda x: x.username, user_cluster_other_members))

  
    other_users_reviews = \
        Review.objects.filter(user_name__in=other_members_usernames) \
            .exclude(restaurant__id__in=user_reviews_restaurant_ids)
    other_users_reviews_restaurant_ids = set(map(lambda x: x.restaurant.id, other_users_reviews))
    
  
    restaurant_list = sorted(
        list(Restaurant.objects.filter(id__in=other_users_reviews_restaurant_ids)), 
        key=lambda x: x.average_rating, 
        reverse=True
    )

    return render(
        request, 
        'reviews/user_recommendation_list.html', 
        {'username': request.user.username,'restaurant_list': restaurant_list}
    )

