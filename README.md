# Django PSI

### Requirements:
- PostgreSQL Database (for JSON fields)
- Google API Dev Credentials

### Settings

1. Add the following settings to your Django project
```python
PSI_GOOGLE_API_DEV_KEY = 'MYKEY'
PSI_SLACK_MESSAGE_HOOK = 'http://myslackmessagehook/zxcvbn'
PROTOCOL = 'HTTP'
DOMAIN = 'www.example-site.com'
ADMIN_PATH = '/admin'
PSI_ENVS = {
    'production': {
        'base_url': 'https://example-site.com',
    },
    'staging': {
        'base_url': 'https://staging-example-site.com',
    }
}
```

2. Add Django PSI to installed apps

```python
INSTALLED_APPS = [
    ...
    'djangopsi',
    ...
]
```

3. Decorate your class-based views with `@is_psi_checked`

```python
from djangopsi.decorators import is_psi_checked


@is_psi_checked
class ExampleView(generic.TemplateView):
    ...
```

4. Run command run_psi_check, or add it to your CI process.

`python manage.py run_psi_check -c -k --slack-message`

Options:

```
-c --console
    Outputs the report in the console

--env=ENV
    Env in which the analysis will be made. Default value is `production`.

-k --keep
    Persist the report to the database

--strategy=STRATEGY
    Strategy to be used on the analysis. Default value is `all` (desktop and mobile).
```


### References

https://developers.google.com/api-client-library/python/apis/pagespeedonline/v5