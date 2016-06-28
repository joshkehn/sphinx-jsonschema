from sphinx import addnodes
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.docfields import GroupedField, TypedField, Field
from sphinx.util.nodes import make_refnode
from sphinx.roles import XRefRole


class JSONObject(ObjectDescription):
    #: Never arguments for Schema objects
    has_arguments = False

    #: what is displayed right before the documentation entry
    display_prefix = None

    def get_index_text(self, objectname, name_obj):
        name, obj = name_obj
        if self.objtype == 'def':
            return _('%s (definition)') % name
        elif self.objtype == 'prop':
            return _('%s (property)') % name
        elif self.objtype == 'schema':
            return _('%s (schema)') % name
        return ''

class JSONDefinition(JSONObject):
    doc_field_types = [
        Field("type", label=l_("Type"), names=("type")),
        TypedField(
            "props", label=l_("Properties"), names=("property", "prop"),
            typenames=("array", "boolean", "integer", "null", "number", "object", "string"),
        )
    ]

    def handle_signature(self, sig, signode):
        import ipdb; ipdb.set_trace()
        signode += addnodes.desc_name(sig, sig)
        fullname = self.objtype.capitalize() + " " + sig
        signode["fullname"] = fullname
        return (fullname, sig)

    def add_target_and_index(self, name_cls, sig, signode):
        signode["ids"].append("{0}-{1}".format(self.objtype, sig))
        self.env.domaindata["jsschema"]["objects"][sig] = (self.env.docname, self.objtype, "")
        # [self.objtype][sig] = (self.env.docname, "")


class JSONSchema(JSONDefinition):
    pass


class JSONProperty(JSONDefinition):
    pass


class JSONXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        # basically what sphinx.domains.python.PyXRefRole does
        refnode['jsschema:object'] = env.ref_context.get('jsschema:object')
        if not has_explicit_title:
            title = title.lstrip('.')
            target = target.lstrip('~')
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target,


class JSONSchemaDomain(Domain):
    name = "jsschema"
    label = "JSONSchema"

    object_types = {
        "definition": ObjType(l_("definition"), "def"),
        "schema": ObjType(l_("schema"), "schema"),
        "property": ObjType(l_("property"), "prop"),
    }

    directives = {
        "def": JSONDefinition,
        "schema": JSONSchema,
        "prop": JSONProperty
    }

    roles = {
        "def": JSONXRefRole(),
        "schema": JSONXRefRole(),
        "prop": JSONXRefRole()
    }

    initial_data = {
        "objects": {},
    }

    def find_obj(self, env, obj, name, typ, searchorder=0):
        objects = self.data["objects"]
        newname = None
        if searchorder == 1:
            if obj and obj + '.' + name in objects:
                newname = obj + '.' + name
            else:
                newname = name
        else:
            if name in objects:
                newname = name
            elif obj and obj + '.' + name in objects:
                newname = obj + '.' + name
        return newname, objects.get(newname)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        # import ipdb; ipdb.set_trace()
        objectname = node.get('jsschema:object')
        searchorder = node.hasattr('refspecific') and 1 or 0
        name, obj = self.find_obj(env, objectname, target, typ, searchorder)
        if not obj:
            return None
        return make_refnode(builder, fromdocname, obj[0],
                            name.replace('$', '_S_'), contnode, name)

    # def resolve_any_xref(self, env, fromdocname, builder, target, node,
    #                      contnode):
    #     objectname = node.get('js:object')
    #     name, obj = self.find_obj(env, objectname, target, None, 1)
    #     if not obj:
    #         return []
    #     return [('js:' + self.role_for_objtype(obj[1]),
    #              make_refnode(builder, fromdocname, obj[0],
    #                           name.replace('$', '_S_'), contnode, name))]

    # def get_objects(self):
    #     for refname, (docname, type) in list(self.data['objects'].items()):
    #         yield refname, refname, type, docname, \
    #             refname.replace('$', '_S_'), 1


def setup(app):
    app.add_domain(JSONSchemaDomain)

