from . import _markdown


class Ten8tStreamlitOverview(_markdown.Ten8tMarkdownOverview):
    """
    Represents an overview component for Ten8t Streamlit application.

    TODO:  This is a placeholder for better support for streamlit
           because it just supports streamlit by being markdown.  Ideally
           this would more fully support streamlit features, color in
           particular.

    To display the output of this class, from streamlit
    md = Ten8tStreamlitOverview(checker).generate()
    st.markdown(md)

    At this time this is only an alias for Ten8tMarkdownOverview, but it is
    assumed that the final code will have streamlit specific functionality.

    """
    pass
