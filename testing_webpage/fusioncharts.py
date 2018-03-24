import json


# Common base class for FC
class FusionCharts:

    constructor_template = """
    <script type="text/javascript">
         FusionCharts.ready(function () {
             new FusionCharts(__constructorOptions__);
         });
    </script>
    """

    render_template = """
    <script type="text/javascript">
         FusionCharts.ready(function () {
             FusionCharts("__chartId__").render();
         });
    </script>
    """

    def __init__(self, type, id, width, height, renderAt, dataFormat, dataSource):
        self.constructor_options = dict()
        self.constructor_options['type'] = type
        self.constructor_options['id'] = id
        self.constructor_options['width'] = width
        self.constructor_options['height'] = height
        self.constructor_options['renderAt'] = renderAt
        self.constructor_options['dataFormat'] = dataFormat
        self.constructor_options['dataSource'] = dataSource

    # render the chart created
    # It prints a script and calls the FusionCharts javascript render method of created chart
    def render(self):
        self.ready_json = json.dumps(self.constructor_options)
        self.ready_json = FusionCharts.constructor_template.replace('__constructorOptions__', self.ready_json)
        self.ready_json = self.ready_json + FusionCharts.render_template.replace('__chartId__', self.constructor_options['id'])
        self.ready_json = self.ready_json.replace('\\n', '')
        self.ready_json = self.ready_json.replace('\\t', '')

        if self.constructor_options['dataFormat'] == 'json':
            self.ready_json = self.ready_json.replace('\\', '')
            self.ready_json = self.ready_json.replace('"{', "{")
            self.ready_json = self.ready_json.replace('}"', "}")
      
        return self.ready_json
