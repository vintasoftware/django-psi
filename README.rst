Django PSI

1. Decorate your class-based views with `@is_psi_checked`

2. Run command run_psi_check
`python manage.py run_psi_check`

Options:

```
-v -vv -vvv
    Verbose mode.

-c --console
    Outputs the report in the console

--env=ENV
    Default value is staging.
```