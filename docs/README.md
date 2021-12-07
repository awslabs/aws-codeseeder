# Building docs

1. Generate `autodoc` stubs

   ```bash
   sphinx-apidoc --ext-autodoc -o source ../aws_codeseeder --force
   ```

1. Build html docs

   ```bash
   make html
   ```
