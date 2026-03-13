from common.base_questionnaire import BaseQuestionnaire
from . import analytics
from . import reporting

class MbiQuestionnaire(BaseQuestionnaire):

    def __init__(self, df):
        super().__init__(df)
        self.scores_df = None
        self.descriptives = None
        self.crosstabs = None

    def clean_data(self):
        self.clean_common_variables()

    def compute_scores(self):
        self.scores_df = analytics.compute_scores(self.cleaned_df)

    def compute_statistics(self):
        self.descriptives = analytics.compute_descriptives(self.scores_df)

    def generate_crosstabs(self):
        self.crosstabs = analytics.generate_crosstabs(self.cleaned_df, self.scores_df)

    def export_excel(self, output_path):
        reporting.export_excel(self, output_path)

    def export_figures(self, output_path):
        reporting.export_figures(self, output_path)

    def export_word(self, output_path):
        reporting.export_word(self, output_path)

    def run_full_analysis(self, output_path):
        self.clean_data()
        self.compute_scores()
        self.compute_statistics()
        self.generate_crosstabs()
        self.export_excel(output_path)
        self.export_figures(output_path)
        self.export_word(output_path)
