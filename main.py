# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import cgi
import webapp2

form= """
    <form method="post">
      What is your birthday?
      <br>
      <label for="month">
        Month
        <input type="text" name="month" value="%(month)s">
      </label>
      <label for="day">
        Day
        <input type="text" name="day" value="%(day)s">
      </label>
      <label for="year">
        Year
        <input type="text" name="year" value="%(year)s">
      </label>
      <div style="color:red">%(error)s</div>


      <br>
      <br>
      <input type="submit">
    </form>
"""

class MainPage(webapp2.RequestHandler):

    def write_form(self, error="", month="", day="", year=""):
        self.response.out.write(form % {"error": error,
                                        "month": cgi.escape(month, quote=True),
                                        "day": cgi.escape(day, quote=True),
                                        "year": cgi.escape(year, quote=True)})

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = valid_month(user_month)
        day = valid_day(user_day)
        year = valid_year(user_year)

        if not (month and day and year):
            self.write_form("That doesn't look valid to me, friend.", user_month, user_day, user_year)
        else:
            self.redirect("/thanks")

class ThanksHandler(webapp2.RequestHandler):
    """docstring for ThanksHandler."""
    def get(self):
        self.response.out.write("Thanks! That's a totally valid day!")



months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']

month_abbvs = dict((m[:3].lower(),m) for m in months)

def valid_month(month):
    if month:
        short_month = month[:3].lower()
        return month_abbvs.get(short_month)

def valid_day(day):
    if day and day.isdigit():
        day_int = int(day)
        if day_int > 0 and day_int < 31:
            return day_int

def valid_year(year):
    if year and year.isdigit():
        year_int = int(year)
        if year_int >= 1900 and year_int <= 2020:
            return year_int

def escape_html(s):
    for (i, o) in (("&", "&amp;"),(">", "&gt;"),("<", "&lt;"),('"', "&quot;")):
        s = s.replace(i, o)
    return s
#class TestHandler(webapp2.RequestHandler):
#    """docstring for TestHandler."""
#    def post(self):
#        q = self.request.get("q")
#        self.response.out.write(q)
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)

app = webapp2.WSGIApplication([
    ('/', MainPage),('/thanks', ThanksHandler)
], debug=True)
