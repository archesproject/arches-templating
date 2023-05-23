# arches-templating

An application to add templating/reporting capabilities to Arches.  

## Installation

Install via pip, arches-templating (forthcoming).  Or install a development version by pulling down the repository and running `pip install` from the local repo directory.

Add the arches_templating module to the project's list of INSTALLED_APPLICATIONS.

Run migrations from your project to install database.

`python manage.py migrate arches_templating`

Add urls to your project's urls.py if you wish to use the built-in view to submit your templates.  

`path("your-base-url-here/", include("arches_templating.urls"))`

Alternatively, you can call the template engine directory and provide your data container and template ID.  

## The Data Container

The data container is a json-based object that is provided to the template engine along with the template ID.  It is referenced by the template designer when creating the template - the paths in the template should match the ones being provided by the data container.

## Adding Templates

Currently, the only way to add templates is via the django admin interface.  Visit the /admin url of your site and upload your templates there.

## Creating Templates

We currently support five base tags.  

* value
* context
* if
* image
* end

Each of these tags requires a "path" attribute and is prefixed by "arches:".  For example:

`<arches:value path="path/in/data/container">`

An `end` tag is required for the `context` and `if` tags.

The `context` tag will change the "context" of its child tags to whatever its path matches within the data container provided to the template engine.  

Functionally, this means that

`<arches:value path="foo/bar">`

and 

```
<arches:context path="foo">
<arches:value path="bar">
<arches:end>
```

are functionally equivalent and referencing the same data within the data container.  

If the context is pointing to an array, this is currently the method being used to render table rows.  

Elements can be optionally rendered by an `if` tag.

```
<arches:if path="foo">
Some optionally rendered content, depending on value at the "foo" path of your data container.
<arches:end>
```

An `image` tag can render an image from a URL or (optionally) a base64 encoded image from the backend.
`<arches:image path=“path_to_image_or_path_to_url”>`


The `if` tag can be inverted by providing an "inverse" attribute set to true.

`<arches:if inverse="true" path="foo">`

Currently powerpoint, word, and spreadsheet templates are supported.  We welcome the addition of more implementations and improvements/bug fixes on the ones that currently exist.

