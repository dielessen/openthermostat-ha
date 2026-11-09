"""Keep rejected native form input visible; no persistence or validation bypass."""
import probatio as vol

def retained_input_schema(flow,schema,user_input):
    if user_input is None:
        return schema
    values=dict(user_input)
    # Missing optional selector means an explicit clear, not reinsertion of its
    # older suggestion. This only changes display hints; validators stay intact.
    for marker in schema.schema:
        if isinstance(marker,vol.Optional) and marker.schema not in values:
            values[marker.schema]=None
    return flow.add_suggested_values_to_schema(schema,values)


# Plan item 1b (the E32 is the source of truth): a Configure form sends only what the user changed in it.
# The form remembers the E32's values it showed; on submit a field still at that value is left alone,
# so a change made on the E32's own page while the form was open is never put back.
def remember_shown(flow,key,value):
    """Remember what form ``key`` showed (a copy of the E32's values when it opened)."""
    shown=getattr(flow,"_e32_shown",None)
    if type(shown) is not dict:
        shown=flow._e32_shown={}
    shown[key]=value
    return value


def shown_value(flow,key,now):
    """What form ``key`` showed, or ``now`` (the E32's value at submit) when it showed nothing."""
    shown=getattr(flow,"_e32_shown",None)
    return shown[key] if type(shown) is dict and key in shown else now
