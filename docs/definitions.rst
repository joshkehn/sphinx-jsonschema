JSONSchema Definitions
======================

.. jsschema:def:: link_rel

    :type: Object
    :prop string rel: Relationship
    :prop string href: Link template
    :required: rel, href

.. jsschema:def:: links

    :type: Array
    :items: :jsschema:def:`link_rel`

.. jsschema:def:: slug

    :type: String
    :pattern: ..

.. jsschema:def:: extra_data

    :type: Object
    :default: {}
