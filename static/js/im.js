(function () {
    $(function () {
        var $attachBoard = $("#attachBoard");
        var $postText = $("#postInputs .textContent");
        var $_postText = $("#postInputs textarea");
        var $postFileInput = $("#postInputs input");
        var $postSubmitBtn = $("#postSubmit");
        var setPostText = function (text) {
            $postText.html(text);
            $_postText.val($postText.html());
        };
        var getPostText = function () {
            return $postText.val();
        };
        $attachBoard.on("click", '.attach-image img', function () {
            if ($(this).hasClass("zoom")) {
                this.src = $(this).data('origin');
                $(this).css({
                    width: "initial",
                    height: 'initial',
                    maxWidth: 'initial',
                    cursor: 'zoom-in'
                }).removeClass("zoom");
            } else {
                $(this).data('origin', this.src);
                this.src = this.src.split("?")[0];
                $(this).css({
                    width: this.naturalWidth,
                    height: 'initial',
                    minWidth: '100px',
                    maxWidth: '100%',
                    cursor: 'zoom-out'
                }).addClass("zoom");
            }
        });

        $attachBoard.height(window.innerHeight - 160);
        $(window).on('resize', function () {
            $attachBoard.height(window.innerHeight - 160);
        });

        var _onContentChange = function () {
            if (getPostText() || $postFileInput.val()) {
                $postSubmitBtn.removeAttr("disabled");
            } else {
                $postSubmitBtn.attr({disabled: "disabled"});
            }
        };
        var _onFileChange = function () {
            _onContentChange();
            setPostText(this.files[0].name);
            console.log(this);
        };

        $postFileInput.change(_onFileChange);
        $postText.keyup(_onContentChange);

    });
})(this);