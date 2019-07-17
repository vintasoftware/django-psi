# Django PSI

### Settings

Add the env settings to your settings.py
```python
PSI_ENVS = {
    'production': {
        'base_url': 'https://splendidspoon.com',
    },
    'staging': {
        'base_url': 'https://splendidspoon-staging.herokuapp.com',
    }
}
```

1. Decorate your class-based views with `@is_psi_checked`

2. Run command run_psi_check

`python manage.py run_psi_check -c`

Options:

```
-c --console
    Outputs the report in the console

--env=ENV
    Env in which the analysis will be made. Default value is `production`.

-k --keep
    Persist the report to the database

--strategy=STRATEGY
    Strategy to be used on the analysis. Default value is `desktop`.
```


### References

https://developers.google.com/api-client-library/python/apis/pagespeedonline/v5