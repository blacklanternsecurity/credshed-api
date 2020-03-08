import io


class Chart:

    def __init__(self, data, title='', limit=10):

        self.data = data
        self.title = title
        self.limit = limit


    def sorted_data(self, key=lambda x: x[-1], reverse=True):
        '''
        Sorts data and truncates if self.limit is set
        Returns labels and values for use in chart
        '''

        sorted_data = sorted(list(self.data.items()), key=key, reverse=reverse)
        labels = [x[0] for x in sorted_data]
        values = [x[-1] for x in sorted_data]

        if self.limit is not None:
            # group overflow into "other"
            labels = labels[:self.limit - 1] + ['other']
            values = values[:self.limit - 1] + [sum(values[self.limit - 1:])]

        return (labels, values)


    @property
    def bytes(self):
        '''
        Override in child class
        '''
        return b''



class Pie(Chart):

    @property
    def bytes(self):
        '''
        Returns pie chart image as PNG bytes
        '''

        theme = 'dark'

        '''
        import plotly.graph_objects as go

        labels = [d[0] for d in self.domains[:self.limit]]
        values = [d[-1] for d in self.domains[:self.limit]]

        # Use `hole` to create a donut-like pie chart
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.layout.title = f'Unique Accounts by Domain (Last {self.days:,} Days)'
        fig.layout.template = 'plotly_dark'

        return fig
        '''
        import matplotlib.pyplot as plot

        labels, values = self.sorted_data()        

        # explode the first pie slice
        explode = (.1,) + (0,) * (len(values) - 1)

        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        fig, ax = plot.subplots()
        pie_chart = ax.pie(values, explode=explode, labels=labels, startangle=90, \
            autopct=lambda p: '{:.0f}'.format(p * sum(values) / 100))

        plot.legend(pie_chart[0], labels, bbox_to_anchor=(1,0.5), loc="center right", bbox_transform=plot.gcf().transFigure)
        pie_title = plot.title(self.title)

        # equal aspect ratio ensures that pie is drawn as a circle.
        ax.axis('equal')

        if theme == 'dark':
            # dark theme
            plot.style.use('dark_background')
            # set label text to white
            for autotext in pie_chart[2]:
                autotext.set_color('white')
            plot.setp(pie_title, color='w')

        #plot.show()
        png_bytes = io.BytesIO()
        plot.savefig(png_bytes, format='png', edgecolor='none', bbox_inches='tight')
        png_bytes.seek(0)

        return png_bytes.read()