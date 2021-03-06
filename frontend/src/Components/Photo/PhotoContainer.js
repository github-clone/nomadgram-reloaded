import React from "react";
import PropTypes from "prop-types";
import { Mutation } from "react-apollo";
import PhotoPresenter from "./PhotoPresenter";
import { TOGGLE_LIKE_IMAGE, ADD_COMMENT } from "./PhotoQueries";

class ToggleLikeMutation extends Mutation {}
class AddCommentMutation extends Mutation {}

export default class PhotoContainer extends React.Component {
  static propTypes = {
    inline: PropTypes.bool.isRequired,
    id: PropTypes.string.isRequired,
    comments: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string.isRequired,
        message: PropTypes.string.isRequired,
        creator: PropTypes.shape({
          username: PropTypes.string.isRequired
        }).isRequired
      })
    ).isRequired,
    creatorAvatar: PropTypes.string.isRequired,
    creatorUsername: PropTypes.string.isRequired,
    location: PropTypes.string,
    files: PropTypes.arrayOf(
      PropTypes.shape({
        url: PropTypes.string.isRequired,
        id: PropTypes.string.isRequired
      }).isRequired
    ).isRequired,
    likeCount: PropTypes.number.isRequired,
    commentCount: PropTypes.number.isRequired,
    caption: PropTypes.string.isRequired,
    createdAt: PropTypes.string.isRequired,
    isLiked: PropTypes.bool.isRequired
  };

  constructor(props) {
    super(props);
    this.state = {
      newComment: "",
      isLiked: props.isLiked,
      likeCount: props.likeCount,
      selfComments: [],
      currentSlide: 1,
      slides: props.files.length
    };
  }

  render() {
    const {
      inline,
      creatorAvatar,
      creatorUsername,
      location,
      files,
      commentCount,
      caption,
      createdAt,
      comments,
      id
    } = this.props;
    const {
      newComment,
      isLiked,
      likeCount,
      selfComments,
      currentSlide
    } = this.state;
    return (
      <AddCommentMutation
        mutation={ADD_COMMENT}
        variables={{ imageId: id, message: newComment }}
        onCompleted={this.addSelfComment}
      >
        {addComment => {
          this.addComment = addComment;
          return (
            <ToggleLikeMutation
              mutation={TOGGLE_LIKE_IMAGE}
              variables={{ imageId: id }}
            >
              {toggleLike => {
                this.toggleLike = toggleLike;

                return (
                  <PhotoPresenter
                    inline={inline}
                    creatorAvatar={creatorAvatar}
                    creatorUsername={creatorUsername}
                    location={location}
                    files={files}
                    likeCount={likeCount}
                    commentCount={commentCount}
                    caption={caption}
                    createdAt={createdAt}
                    comments={comments}
                    updateNewComment={this.updateNewComment}
                    newComment={newComment}
                    isLiked={isLiked}
                    onLikeClick={this.onLikeClick}
                    selfComments={selfComments}
                    onKeyUp={this.onKeyUp}
                    currentSlide={currentSlide}
                    onNextClick={this.onNextClick}
                    onPreviousClick={this.onPreviousClick}
                  />
                );
              }}
            </ToggleLikeMutation>
          );
        }}
      </AddCommentMutation>
    );
  }

  updateNewComment = event => {
    const {
      target: { value }
    } = event;
    this.setState({
      newComment: value
    });
  };

  onKeyUp = event => {
    const { keyCode } = event;
    if (keyCode === 13) {
      this.addComment();
    } else {
      return;
    }
  };

  onLikeClick = () => {
    const { likeCount, isLiked } = this.props;
    this.toggleLike();
    this.setState(state => {
      let likeNumber;
      if (!isLiked) {
        if (likeCount === state.likeCount) {
          likeNumber = likeCount + 1;
        } else {
          likeNumber = likeCount;
        }
      } else {
        if (likeCount === state.likeCount) {
          likeNumber = likeCount - 1;
        } else {
          likeNumber = likeCount;
        }
      }
      return {
        isLiked: !state.isLiked,
        likeCount: likeNumber
      };
    });
  };

  addSelfComment = data => {
    const { newComment } = this.state;
    const {
      addComment: { comment }
    } = data;
    if (comment) {
      this.setState(state => {
        return {
          selfComments: [
            ...state.selfComments,
            {
              id: comment.id,
              username: comment.creator.username,
              message: newComment
            }
          ],
          newComment: ""
        };
      });
    }
  };

  onNextClick = () => {
    const { slides, currentSlide } = this.state;
    console.log(slides, currentSlide);
    if (currentSlide === slides) {
      this.setState({
        currentSlide: 1
      });
    } else {
      this.setState(state => {
        return {
          currentSlide: state.currentSlide + 1
        };
      });
    }
  };

  onPreviousClick = () => {
    const { slides, currentSlide } = this.state;
    if (currentSlide === slides) {
      this.setState({
        currentSlide: 1
      });
    } else {
      this.setState(state => {
        return {
          currentSlide: state.currentSlide - 1
        };
      });
    }
  };
}
