# Building docs

1. Generate `autodoc` stubs when new modules are added

   ```bash
   sphinx-apidoc --ext-autodoc -o source ../aws_codeseeder --force
   ```

1. Build html docs

   ```bash
   make html
   ```
