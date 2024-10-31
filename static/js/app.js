const socket = io();

// Real-time comments
socket.on('new_comment', (comment) => {
    const commentsContainer = document.getElementById('comments');
    const commentElement = document.createElement('div');
    commentElement.className = 'comment slide-up';
    commentElement.innerHTML = `
        <strong>${comment.username}</strong>
        <p>${comment.content}</p>
        <small>${new Date(comment.created_at).toLocaleString()}</small>
    `;
    commentsContainer.appendChild(commentElement);
});

// Social media sharing
function shareGallery(platform, url, title) {
    const shareUrls = {
        twitter: `https://twitter.com/intent/tweet?url=${url}&text=${title}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
        linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`
    };
    
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
}

// Media upload preview
function previewMedia(input, previewContainer) {
    if (input.files) {
        [...input.files].forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.createElement('div');
                preview.className = 'media-preview zoom-in';
                
                if (file.type.startsWith('image/')) {
                    preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                } else if (file.type.startsWith('video/')) {
                    preview.innerHTML = `<video src="${e.target.result}" controls></video>`;
                }
                
                previewContainer.appendChild(preview);
            };
            reader.readAsDataURL(file);
        });
    }
}