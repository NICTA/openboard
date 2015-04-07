from django.db import models

# Create your models here.

class BeachSummaryHistory(models.Model):
    SYDNEY_OCEAN = 'SYDOC'
    SYDNEY_HARBOUR = 'SYDHB'
    BOTANY_BAY = 'BOTNY'
    PITTWATER = 'PIWAT'
    CENTRAL_COAST = 'CTRCT'
    ILLAWARRA = 'ILLAW'
    HUNTER = 'HUNTR'
    regions = {
        SYDNEY_OCEAN: 'Sydney Ocean',
        SYDNEY_HARBOUR: 'Sydney Harbour',
        BOTANY_BAY: 'Botany Bay, Georges River and Port Hacking',
        PITTWATER: 'Pittwater',
        CENTRAL_COAST: 'Central Coast',
        ILLAWARRA: 'Illawarra',
        HUNTER: 'Hunter',
    }
    sort_orders = {
        SYDNEY_OCEAN: 1000,
        SYDNEY_HARBOUR: 2000,
        BOTANY_BAY: 3000,
        PITTWATER: 4000,
        CENTRAL_COAST: 5000,
        ILLAWARRA: 6000,
        HUNTER: 7000,
    }
    day=models.DateField(auto_now=True)
    region=models.CharField(max_length=5, choices=regions.items())
    num_pollution_unlikely=models.IntegerField()
    num_pollution_possible=models.IntegerField()
    num_pollution_likely=models.IntegerField()
    @classmethod
    def sydney_beaches(cls):
        return (cls.SYDNEY_OCEAN,
                                cls.SYDNEY_HARBOUR,
                                # cls.BOTANY_BAY,
                                # cls.PITTWATER,
        )
    @classmethod
    def ocean_beaches(cls):
        return (cls.SYDNEY_OCEAN,
                    cls.CENTRAL_COAST,
                    cls.ILLAWARRA,
                    cls.HUNTER)
    def is_sydney(self):
        return self.region in (self.SYDNEY_OCEAN,
                                self.SYDNEY_HARBOUR,
                                # self.BOTANY_BAY,
                                # self.PITTWATER,
        )
                            
    def region_display(self):
        return self.regions[self.region]
    def __unicode__(self):
        return "%s %s: +%d %d %d-" % (self.region_display(),
                                    self.day.strftime("%d/%m/%Y"),
                                    self.num_pollution_unlikely,
                                    self.num_pollution_possible,
                                    self.num_pollution_likely)
    class Meta:
        unique_together=(("day", "region"),)
        ordering = ("day", "region")

class CurrentBeachRating(models.Model):
    GOOD=1
    FAIR=2
    POOR=3
    ratings = [ "-", 
                "Pollution is unlikely. Enjoy your swim!",
                "Pollution is possible. Take care.",
                "Pollution is likely. Avoid swimming today.",
    ]
    region=models.CharField(max_length=5, choices=BeachSummaryHistory.regions.items())
    beach_name=models.CharField(max_length=100)
    rating=models.SmallIntegerField(choices=(
                    (GOOD, ratings[GOOD]),
                    (FAIR, ratings[FAIR]),
                    (POOR, ratings[POOR]),
                ))
    day_updated=models.DateField(auto_now=True)
    def region_display(self):
        return BeachSummaryHistory.regions[self.region]
    def rating_display(self):
        return self.ratings[self.rating]
    def __unicode__(self):
        return "%s (%s): %s" % (self.beach, 
                        self.region_display(), self.rating_display())
    def parse_advice(self, advice):
        if "unlikely" in advice:
            return self.GOOD
        elif "possible" in advice:
            return self.FAIR
        else:
            return self.GOOD
    class Meta:
        unique_together=(("region", "beach_name"),)
        ordering=("region", "beach_name", "-rating")

