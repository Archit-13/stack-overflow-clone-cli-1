from models import postsModel
from views import postsView
from models import authModel

class PostsController:
	def __init__(self, pathToDB):
		self.model = postsModel.PostsModel(pathToDB)
		self.view = postsView.PostsView()
		self.pathToDB = pathToDB

	def run(self, uid, pid):
		"""
		Runs through the post action process
		"""

		userIsPrivileged = authModel.AuthModel(self.pathToDB).checkIfUserIsPrivileged(uid)
		postIsQuestion = self.model.checkIfPostIsQuestion(pid)

		postAction = ''
		while postAction != 'Back':
			userHasVotedOnPost = self.model.checkIfUserHasVotedOnPost(pid, uid)
			postIsAcceptedAnswer = not postIsQuestion and self.model.checkIfAnswerIsAccepted(pid)

			if(not postIsQuestion):
				linkedQ,linkedQDetails,max_len = self.model.getLinkedQuestion(pid)
			else:
				linkedQ=''

			# Prompts the user for the action they want to perform on the post
			postAction = self.view.getPostAction(
				postIsQuestion,
				userHasVotedOnPost,
				userIsPrivileged,postIsAcceptedAnswer,linkedQ
			)
			if(postAction == {} ):
				self.view.logMessage("#ERROR: Don't Click on the Options, Try again with keystrokes")
				continue
			postAction = postAction['post action']

			

			if postAction == 'Upvote Post':
				self.model.addVoteToPost(pid, uid)
				self.view.logMessage("Successfully upvoted post")

			elif postAction == ('Linked Question: ' +linkedQ):
				self.view.showLinkedQ(linkedQDetails,max_len)
				self.run(uid,linkedQ)
				pass

			elif postAction == 'Answer Question':
				postValues = self.view.getAnswerPostValues()
				title = postValues['title']
				body = postValues['body']
				postCreationIsSuccessful = self.model.createAnswer(title, body, pid, uid)

				if postCreationIsSuccessful:
					self.view.logMessage("Successfully added your answer")
				else:
					self.view.logMessage("Failed to add your answer")

			elif postAction == 'Give Badge to Poster':
				possibleBadges = self.model.getBadgeNames()

				if possibleBadges == []:
					self.view.logMessage("#ERROR: There are no badges to give away")
					continue

				# Get the Badge details from user
				badgeValues = self.view.getBadgeValues(possibleBadges)
				if("bName" not in badgeValues):
					self.view.logMessage("#ERROR: Don't Click on the Options, Try again with keystrokes")
					continue

				bName = badgeValues['bName']

				# Add the badge to the database and to the poster if not already there
				badge_exists = self.model.addBadgeToPoster(bName, pid, userIsPrivileged)

				if(badge_exists == -2):
					self.view.logMessage("#ERROR: User got this Badge today already, Try again tomorrow")
					continue
				self.view.logMessage("Successfully gave badge to poster")

			elif postAction == 'Add Tag to Post':
				#Get the Tag value from user
				tagValue = self.view.getTagValue()
				#Add the Tag to the database if not already there
				tag_exists = self.model.addTagToPost(tagValue,pid,userIsPrivileged)
				if(tag_exists):
					self.view.logMessage("#ERROR: Tag already exists, Enter another tag name")
					continue
				self.view.logMessage("Successfully tagged the post")

			elif postAction == 'Mark Answer As Accepted':
				qid = self.model.getQuestionAnsweredByPost(pid)

				questionHasAcceptedAnswer = self.model.checkIfQuestionHasAnAcceptedAnswer(qid)

				if questionHasAcceptedAnswer:
					overwriteAcceptedAnswer = self.view.promptToOverwriteAcceptedAnswer()

					if overwriteAcceptedAnswer:
						self.model.markAnswerAsAccepted(qid, pid, userIsPrivileged)
				else:
					self.model.markAnswerAsAccepted(qid, pid, userIsPrivileged)

			elif postAction == 'Edit Post':
				postValues = self.view.getPostValues()
				self.model.editPost(pid, postValues['title'], postValues['body'])
				self.view.logMessage("Post editted successfully")
