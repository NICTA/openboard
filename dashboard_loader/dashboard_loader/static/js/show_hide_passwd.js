function showHidePasswordFields(show) {
        $ = django.jQuery;
        if (show) {
                if ($('tr[id=password1]').hasClass('hidden')) {
                        $('tr[id^=password]').removeClass('hidden');
                }
        } else {
                if (!$('tr[id=password1]').hasClass('hidden')) {
                        $('tr[id^=password]').addClass('hidden');
                }
        };
};

function showHidePasswordFieldsFromRadioButton(name) {
        $ = django.jQuery;
        butval = $('input[name=' + name +']:checked').val();
        if (butval == '3') {
		showHidePasswordFields(true);
        } else {
		showHidePasswordFields(false);
        };
};

