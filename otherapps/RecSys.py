from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from django.templatetags.static import static


class RecSys:
    """
    Recommends Jobs or jobseekers depending on the mode using TF_IDF Vectorization and Cosine Similarity.

    Attributes:
        jobs(dataframe): All the Job Details.
        jobseekers(dataframe): All the JobSeekers Details.
    """
    def __init__(self):
        self.skills = {}
        # THIS IS JUST A DUMMY DATASET. Please change it later.
        self.jobs = pd.read_json(Path.cwd().joinpath('newnormal/static/assets/jobs.json'), orient ="columns")
  
        # Adding an ID Column. Remove the below line if ID already exists
        self.jobs['id'] = [x for x in range(self.jobs.shape[0])]

        # THIS IS JUST A DUMMY DATASET. Please change it later.
        self.jobseekers = pd.read_json(Path.cwd().joinpath('newnormal/static/assets/jobseekers.json'), orient ="columns")
        # Adding an ID Column. Remove the below line if ID already exists.
        self.jobseekers['id'] = [x for x in range(self.jobseekers.shape[0])]

        self.jobs['jobtitle'] = self.jobs['jobtitle'].astype('str')
        self.jobs['jobdescription'] = self.jobs['jobdescription'].astype('str')
        self.jobs['skills'] = self.jobs['skills'].astype('str')

        self.jobseekers['Name'] = self.jobseekers['Name'].astype('str')
        self.jobseekers['Description'] = self.jobseekers['Description'].astype('str')
        self.jobseekers['Skills'] = self.jobseekers['Skills'].astype('str')

        # Combing multiple columns into one to make feature selections much easier.
        # Add or remove columns that had to be trained as a feature.
        # Eg: In self.jobs the columns Title, Descrition and the Skills are selected as features to make prediction.
        self.jobs['content'] = self.jobs[['jobtitle', 'jobdescription', 'skills']].astype(str).apply(lambda x: ' // '.join(x), axis = 1)
        self.jobseekers['content'] = self.jobseekers[['Skills', 'Description']].astype(str).apply(lambda x: ' // '.join(x), axis = 1)

        self.jobs['content'].fillna('', inplace = True)
        self.jobseekers['content'].fillna('', inplace = True)


    def _find_similar(self, mode):
        """
        Returns the Recommended Jobs or jobseekers depending on the mode.

        Args:
            mode (str['jobs', 'jobseekers']): The type of Recommendation. The mode has to be either 'jobs' or 'jobseekers'

        Raises:
            ValueError: Invalid mode.

        Returns:
            list: Recommended jobs or jobseekers.
        """
        

        if mode.lower() == 'jobs':
            tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english', lowercase=True)
            jobseekers_tfidf_matrix = tf.fit_transform(self.jobs['content'])
            jobs_tfidf_matrix = tf.transform(self.skills['content'])

            cosine_similarities = linear_kernel(jobseekers_tfidf_matrix, jobs_tfidf_matrix)

            results = []
            for idx, row in self.jobs.iterrows():
                similar_indices = cosine_similarities[idx].argsort()
                similar_items = [(cosine_similarities[idx][i], self.skills['id'][0]) for i in similar_indices]
                for x in similar_items:
                  if x[0]: results.append((idx, x[0]))
            results.sort(key=lambda z: z[1], reverse=True)
            return results

        elif mode.lower() == 'jobseekers':
            tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english', lowercase=True)
            jobs_tfidf_matrix = tf.fit_transform(self.jobseekers['content'])
            jobseekers_tfidf_matrix = tf.transform(self.skills['content'])

            cosine_similarities = linear_kernel(jobs_tfidf_matrix, jobseekers_tfidf_matrix)

            results = []
            for idx, row in self.jobseekers.iterrows():
                similar_indices = cosine_similarities[idx].argsort()
                similar_items = [(cosine_similarities[idx][i], self.skills['id'][0]) for i in similar_indices]
                for x in similar_items:
                  if x[0]: results.append((idx, x[0]))
            results.sort(key=lambda z: z[1], reverse=True)
            return results

        else:
            raise ValueError('Invalid Mode: ' + mode)


    def _get_job(self, id):
        """
        Returns the Job details in a cleaner way.

        Args:
            id (int): Job ID representing a specific job.

        Returns:
            dict: Job detail respective to the give ID.
        """
        name   = self.jobs.loc[self.jobs['id'] == id]['jobtitle'].tolist()[0]
        desc   = self.jobs.loc[self.jobs['id'] == id]['jobdescription'].tolist()[0]
        skills = self.jobs.loc[self.jobs['id'] == id]['skills'].tolist()[0]
        job = {
        'name': name,
        'skills': skills,
        'description': desc,
        }
        return job



    def _get_jobseeker(self, id):
        """
        Returns the JobSeekers details in a cleaner way.

        Args:
            id (int): JobSeeker ID representing a specific jobseeker.

        Returns:
            str: JobSeeker detail respective to the give ID.
        """
        name   = self.jobseekers.loc[self.jobseekers['id'] == id]['Name'].tolist()[0]
        desc   = self.jobseekers.loc[self.jobseekers['id'] == id]['Description'].tolist()[0]
        skills = self.jobseekers.loc[self.jobseekers['id'] == id]['Skills'].tolist()[0]
        jobseeker = {
        'name': name,
        'skills': skills,
        'description': desc,
        }
        return jobseeker



    def _parse_keywords(self, keywords):
      """
      Converts the list of keywords into a Dataframe.

      Args:
          keywords (list): The collection of all keywords from user.

      """
      # Converting the keywords into a Dataframe to use it for prediction
      self.skills = pd.DataFrame([keywords], columns=["skills"])
      self.skills['id'] = [x for x in range(self.skills.shape[0])]
      
      self.skills['content'] = self.skills[['skills']].astype(str).apply(lambda x: ' // '.join(x), axis = 1)
      self.skills['content'].fillna('', inplace = True)

      return None


    def recommended(self, keywords, mode):
        """
        Returns a list of all recommended Jobs or jobseekers.

        Args:
            keywords (list): The search keywords entered by the user.
            mode (str['jobs', 'jobseekers']): The type of Recommendation. The mode has to be either 'jobs' or 'jobseekers'.

        Raises:
            ValueError: Invalid mode.

        Returns:
            list: all the recommended Jobs or jobseekers.
        """

        self._parse_keywords(keywords)

        if mode.lower() == 'jobs':
            similar_jobs = self._find_similar(mode)
            return [self._get_job(rec[0]) for rec in similar_jobs]

        elif mode.lower() == 'jobseekers':
            similar_jobseekers = self._find_similar(mode)
            return [self._get_jobseeker(rec[0]) for rec in similar_jobseekers]
            
        else:
            raise ValueError('Invalid Mode: ' + mode)
