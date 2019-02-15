# Django PSI

### Settings

Add the env settings to your settings.py
```
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
-v -vv -vvv
    Verbose mode.

-c --console
    Outputs the report in the console

--env=ENV
    Default value is staging.
```


### References

https://developers.google.com/api-client-library/python/apis/pagespeedonline/v5