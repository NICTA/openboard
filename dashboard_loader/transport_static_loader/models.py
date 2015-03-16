import datetime
import decimal
from django.db import models

from dashboard_loader.loader_utils import LoaderException
# Create your models here.

class Agency(models.Model):
    agency_id = models.CharField(max_length=10, unique=True)
    agency_name = models.CharField(max_length=200)
    def __unicode__(self):
        return "%s (%s)" % (agency_id, agency_name)
    @classmethod
    def load_csv_row(cls, row):
        agency_id=row[0]
        try:
            agency = cls.objects.get(agency_id=agency_id)
        except cls.DoesNotExist:
            agency = cls(agency_id=agency_id)
        agency.agency_name = row[1] 
        return agency
    def unique_key(self):
        return self.agency_id
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(agency_id=key)

class Calendar(models.Model):
    service_id = models.CharField(max_length=20, unique=True)
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    def set_dates(self, start_ds, end_ds):
        self.start_date = datetime.datetime(int(start_ds[0:4]),
                                            int(start_ds[4:6]),
                                            int(start_ds[6:8]))
        self.end_date = datetime.datetime(int(end_ds[0:4]),
                                            int(end_ds[4:6]),
                                            int(end_ds[6:8]))
    def service_is_active(self, date):
        if date >= self.start_date and date <= self.end_date:
            try:
                self.calendardate_set.get(exception_date=date, exception_type=CalendarDate.REMOVED)
                return False
            except CalendarDate.DoesNotExist:
                return True
        else:
            try:
                self.calendardate_set.get(exception_date=date, exception_type=CalendarDate.ADDED)
                return True
            except CalendarDate.DoesNotExist:
                return False
    @classmethod
    def load_csv_row(cls, row):
        service_id = row[0]
        try:
            calendar = cls.objects.get(service_id=service_id)
        except cls.DoesNotExist:
            calendar = cls(service_id=service_id)
        calendar.monday = bool(int(row[1]))
        calendar.tuesday = bool(int(row[2]))
        calendar.wednesday = bool(int(row[3]))
        calendar.thursday = bool(int(row[4]))
        calendar.friday = bool(int(row[5]))
        calendar.saturday = bool(int(row[6]))
        calendar.sunday = bool(int(row[7]))
        calendar.set_dates(row[8], row[9])
        return calendar
    def unique_key(self):
        return self.service_id
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(service_id=key)

class CalendarDate(models.Model):
    ADDED = 1
    REMOVED = 2
    exception_types = {
        ADDED: "Added",
        REMOVED: "Removed"
    }
    calendar = models.ForeignKey(Calendar)
    exception_date = models.DateField()
    exception_type = models.SmallIntegerField(choices=exception_types.items())
    class Meta:
        unique_together=(('calendar', 'exception_date'),)
        ordering = ('calendar', 'exception_date')
    @classmethod
    def load_csv_row(cls, row):
        service_id = row[0]
        date = datetime.date(int(row[1][0:4]), int(row[1][4:6]), int(row[1][6:8]))
        try:
            cd = cls.objects.get(calendar__service_id=service_id, exception_date=date)
        except cls.DoesNotExist:
            cd = cls(calendar=Calendar.objects.get(service_id=service_id),
                    exception_date=date)
        cd.exception_type=int(row[2])
        return cd
    def unique_key(self):
        return (self.calendar.service_id, self.exception_date)
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(calendar__service_id=key[0], 
                    exception_date=key[1])

class Route(models.Model):
    SVC_LIGHTRAIL = 0
    SVC_SUBWAY = 1
    SVC_TRAIN = 2
    SVC_BUS = 3
    SVC_FERRY = 4
    service_types = {
        SVC_LIGHTRAIL: "Light Rail Service",
        SVC_SUBWAY: "Subway Service",
        SVC_TRAIN: "Train Service",
        SVC_BUS: "Bus Service",
        SVC_FERRY: "Ferry Service",
    }
    route_id = models.CharField(max_length=20, unique=True)
    agency = models.ForeignKey(Agency)
    short_name = models.CharField(max_length=50, null=True, blank=True)
    long_name = models.CharField(max_length=500)
    network = models.CharField(max_length=200)
    service_type = models.SmallIntegerField(choices=service_types.items())
    colour=models.CharField(max_length=6)
    text_colour=models.CharField(max_length=6)
    @classmethod
    def load_csv_row(cls, row):
        route_id = row[0]
        try:
            route = cls.objects.get(route_id=route_id)
        except cls.DoesNotExist:
            route = cls(route_id=route_id)
        route.agency = Agency.objects.get(agency_id=row[1])
        if row[2]:
            route.short_name = row[2]
        else:
            route.short_name = None
        route.long_name = row[3]
        route.network = row[4]
        route.service_type = int(row[5])
        route.colour = row[6]
        route.text_colour = row[7]
        return route
    def unique_key(self):
        return self.route_id
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(route_id=key)

# class Shape(models.Model):

class Stop(models.Model):
    stop_id = models.CharField(max_length=20, unique=True)
    transit_stop_number = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=16, decimal_places=13)
    longitude = models.DecimalField(max_digits=16, decimal_places=13)
    is_parent_station = models.BooleanField(default=False)
    parent_station = models.ForeignKey("self", null=True, blank=True)
    wheelchair_boarding = models.NullBooleanField()
    platform_number = models.CharField(max_length=50, null=True, blank=True)
    def set_wheelchair_boarding(self, val):
        if int(val) == 1:
            self.wheelchair_boarding = True
        elif int(val) == 2:
            self.wheelchair_boarding = False
        else:
            self.wheelchair_boarding = None
    @classmethod
    def load_csv_row(cls, row):
        stop_id = row[0]
        try:
            stop = cls.objects.get(stop_id=stop_id)
        except cls.DoesNotExist:
            stop = cls(stop_id=stop_id)
        if row[1]:
            stop.transit_stop_number=int(row[1])
        else:
            stop.transit_stop_number = None
        stop.name=row[2]
        stop.latitude=decimal.Decimal(row[3])
        stop.longitude=decimal.Decimal(row[4])
        if row[5]:
            stop.is_parent_station = True
        else:
            stop.is_parent_station = False
        if row[6]:
            try:
                stop.parent_station = cls.objects.get(stop_id=row[6])
            except cls.DoesNotExist:
                # Have to leave it until next load :(
                stop.parent_station = None
        else:
            stop.parent_station = None
        stop.set_wheelchair_boarding(row[7])
        if row[8]:
            stop.platform_number=row[8]
        else:
            stop.platform_number=None
        return stop
    def unique_key(self):
        return self.stop_id
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(stop_id=key)

class Trip(models.Model):
    trip_id = models.CharField(max_length=50, unique=True)
    route = models.ForeignKey(Route)
    calendar = models.ForeignKey(Calendar)
    shape_id = models.CharField(max_length=50)
    headsign = models.CharField(max_length=200)
    main_direction = models.BooleanField(default=False)
    block_id = models.CharField(max_length=20, null=True, blank=True)
    wheelchair_accessible = models.NullBooleanField()
    def set_wheelchair_accessible(self, val):
        if int(val) == 1:
            self.wheelchair_accessible = True
        elif int(val) == 2:
            self.wheelchair_accessible = False
        else:
            self.wheelchair_accessible = None
    @classmethod
    def load_csv_row(cls, row):
        trip_id = row[2]
        try:
            trip = cls.objects.get(trip_id=trip_id)
        except cls.DoesNotExist:
            trip = cls(trip_id=trip_id)
        trip.route = Route.objects.get(route_id=row[0])
        trip.calendar = Calendar.objects.get(service_id=row[1])
        trip.shape_id = row[3]
        trip.headsign = row[4]
        trip.main_direction = bool(int(row[5]))
        if row[6]:
            trip.block_id = row[6]
        else:
            trip.block_id = None
        trip.set_wheelchair_accessible(row[7])
        return trip
    def unique_key(self):
        return self.trip_id
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(trip_id=key)

class StopTime(models.Model):
    REGULAR_SCHED = 0
    NOT_AVAILABLE = 1
    PHONE_REQUIRED = 2
    COORD_REQUIRED = 3
    pickup_dropoff_types = {
        REGULAR_SCHED: "Regularly scheduled pickup/dropoff",
        NOT_AVAILABLE: "No pickup/dropoff available",
        PHONE_REQUIRED: "Must phone agency to arrange pickup/dropoff",
        COORD_REQUIRED: "Must coordinate with driver to arrange pickup/dropoff",
    }
    trip = models.ForeignKey(Trip)
    stop = models.ForeignKey(Stop)
    stop_sequence = models.SmallIntegerField()
    arrival_time_day_offset=models.SmallIntegerField(default=0)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time_day_offset=models.SmallIntegerField(default=0)
    departure_time = models.TimeField(null=True, blank=True)
    headsign = models.CharField(max_length=200, null=True, blank=True)
    pickup_type = models.SmallIntegerField(choices=pickup_dropoff_types.items())
    dropoff_type = models.SmallIntegerField(choices=pickup_dropoff_types.items())
    shape_dist_travelled = models.DecimalField(max_digits=16, decimal_places=10, null=True, blank=True)
    def set_arrival_time(self, val):
        (time, offset) = self.parse_time_val(val)
        self.arrival_time = time
        self.arrival_time_day_offset = offset
    def set_departure_time(self, val):
        (time, offset) = self.parse_time_val(val)
        if time == None:
            self.departure_time = time
            self.departure_time_day_offset = offset
        else:
            self.departure_time = self.arrival_time
            self.departure_time_day_offset = self.arrival_time_day_offset
    def parse_time_val(self, val):
        if not val:
            return (None, 0)
        bits = val.split(":")
        if len(bits) != 3:
            raise LoaderException("Illegal time value: %s" % val)
        hour = int(bits[0])
        mins = int(bits[1])
        secs = int(bits[2])
        if hour >= 24:
            offset = hour / 24
            hour = hour % 24
        else:
            offset = 0
        return (datetime.time(hour,mins,secs), offset)
    @classmethod
    def load_csv_row(cls, row):
        trip_id = row[0]
        stop_sequence = row[4]
        try:
            st = cls.objects.get(trip__trip_id=trip_id, 
                                stop_sequence=stop_sequence)
        except cls.DoesNotExist:
            st = cls(trip=Trip.objects.get(trip_id=trip_id), 
                                stop_sequence=stop_sequence)
        st.stop = Stop.objects.get(stop_id=row[3])
        st.set_arrival_time(row[1])
        st.set_departure_time(row[2])
        if row[5]:
            st.headsign=row[5]
        else:
            st.headsign=None
        st.pickup_type = int(row[6])
        st.dropoff_type = int(row[7])
        if row[8]:
            st.shape_dist_travelled=decimal.Decimal(row[8])
        else:
            st.shape_dist_travelled=None
        return st
    def unique_key(self):
        return (self.trip.trip_id, self.stop_sequence)
    @classmethod
    def get_by_unique_key(cls, key):
        return cls.objects.get(trip__trip_id=key[0], stop_sequence=key[1])
    class Meta:
        unique_together=[("trip", "stop_sequence")]
        ordering = ("trip", "stop_sequence")

