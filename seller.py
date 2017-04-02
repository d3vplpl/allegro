class Seller:


    def __init__(self, seller_id, seller_name, seniority, no_of_feedbacks, last_logged, feedbacks_diversity, positive_feed_cost):
        self.seller_id  = seller_id
        self.seller_name = seller_name
        self.senior = seniority
        self.feedbacks_count = no_of_feedbacks
        self.last_logged = last_logged
        self.feedbacks_diversity = feedbacks_diversity
        self.cumulative_positive_feed_cost = positive_feed_cost #meaning how much money spent on positive feedbacks