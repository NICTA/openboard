/************************************

  Copyright 2015 NICTA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

************************************/

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

