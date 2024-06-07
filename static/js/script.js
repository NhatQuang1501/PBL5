window.addEventListener("load", function() {
    document.querySelector(".preloader").classList.add("opacity-0");
    setTimeout(function() {
        document.querySelector(".preloader").style.display = "none";

        // Tìm nút bộ lọc mặc định bằng cách chọn nút có giá trị "data-filter" là "web-design" (hoặc giá trị mặc định mà bạn muốn)
        const defaultFilterBtn = filterContainer.querySelector('[data-filter="web-design"]');

        if (defaultFilterBtn) {
            // Nếu tìm thấy nút bộ lọc mặc định, đánh dấu nó là "active"
            defaultFilterBtn.classList.add("active");

            // Lấy giá trị "data-filter" của nút bộ lọc mặc định
            const defaultFilterValue = defaultFilterBtn.getAttribute("data-filter");

            // Lặp qua tất cả các mục trong danh sách portfolio và ẩn các mục không khớp với bộ lọc mặc định
            for (let k = 0; k < totalPortfolioItem; k++) {
                const itemCategory = portfolioItems[k].getAttribute("data-category");
                if (defaultFilterValue !== "all" && defaultFilterValue !== itemCategory) {
                    portfolioItems[k].classList.add("hide");
                }
            }
        }
    }, 1000);
});


// Portfolio Item Filter
const filterContainer = document.querySelector(".portfolio-filter"),
    filterBtns = filterContainer.children,
    totalFilterBtn = filterBtns.length,
    portfolioItems = document.querySelectorAll(".portfolio-item"),
    totalPortfolioItem = portfolioItems.length;

for (let i = 0; i < totalFilterBtn; i++) {
    filterBtns[i].addEventListener("click", function() {
        filterContainer.querySelector(".active").classList.remove("active")
        this.classList.add("active");

        const filterValue = this.getAttribute("data-filter");
        for (let k = 0; k < totalPortfolioItem; k++) {
            if (filterValue === portfolioItems[k].getAttribute("data-category")) {
                portfolioItems[k].classList.remove("hide");
                portfolioItems[k].classList.add("show");
            } else {
                portfolioItems[k].classList.remove("show")
                portfolioItems[k].classList.add("hide")
            }

        }

    })
}



// Portfolio Lightbox

// const lightbox = document.querySelector(".lightbox"),
//     lightboxImg = lightbox.querySelector(".lightbox-img"),
//     lightboxClose = lightbox.querySelector(".lightbox-close"),
//     lightboxText = lightbox.querySelector(".caption-text"),
//     lightboxCounter = lightbox.querySelector(".caption-counter");
// let itemIndex = 0;

// for (let i = 0; i < totalPortfolioItem; i++) {
//     portfolioItems[i].addEventListener("click", function() {
//         itemIndex = i;
//         changeItem();
//         toggleLightbox();
//     })
// }

// function nextItem() {
//     if (itemIndex === totalPortfolioItem - 1) {
//         itemIndex = 0
//     } else {
//         itemIndex++
//     }
//     changeItem()
// }

// function prevItem() {
//     if (itemIndex === 0) {
//         itemIndex = totalPortfolioItem - 1
//     } else {
//         itemIndex--;
//     }
//     changeItem()
// }
// //Body.......
// function toggleLightbox() {
//     lightbox.classList.toggle("open");
// }

function changeItem() {
    // imgSrc = portfolioItems[itemIndex].querySelector(".portfolio-img img").getAttribute("src");
    // lightboxImg.src = imgSrc;
    // lightboxText.innerHTML = portfolioItems[itemIndex].querySelector("h4").innerHTML;
    // lightboxCounter.innerHTML = (itemIndex + 1) + " of " + totalPortfolioItem;
}

// Close Lightbox
// lightbox.addEventListener("click", function(event) {
//     if (event.target === lightboxClose || event.target === lightbox) {
//         toggleLightbox();
//     }

// })


// Aside Navbar

const nav = document.querySelector(".nav"),
    navList = nav.querySelectorAll("li"),
    totalNavList = navList.length,
    allSection = document.querySelectorAll(".section"),
    totalSection = allSection.length;

for (let i = 0; i < totalNavList; i++) {
    const a = navList[i].querySelector("a");
    a.addEventListener("click", function() {
        // remove back secion
        removeBackSectionClass();

        for (let i = 0; i < totalSection; i++) {
            allSection[i].classList.remove("back-section");
        }


        for (let j = 0; j < totalNavList; j++) {
            if (navList[j].querySelector("a").classList.contains("active")) {
                // add back section
                addBackSectionClass(j);
            }
            navList[j].querySelector("a").classList.remove("active")
        }
        this.classList.add("active")
        showSection(this);
        if (window.innerWidth < 1200) {
            asideSectionTogglerBtn();
        }
    })

}

function removeBackSectionClass() {
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.remove("back-section")
    }
}

function addBackSectionClass(num) {
    allSection[num].classList.add("back-section");
}

function showSection(element) {
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.remove("active");
    }
    const target = element.getAttribute("href").split("#")[1];
    document.querySelector("#" + target).classList.add("active")

}

function updateNav(element) {
    for (let i = 0; i < totalNavList; i++) {
        navList[i].querySelector("a").classList.remove("active");
        const target = element.getAttribute("href").split("#")[1];
        if (target === navList[i].querySelector("a").getAttribute("href").split("#")[1]) {
            navList[i].querySelector("a").classList.add("active");
        }
    }
}

// document.querySelector(".hire-me").addEventListener("click", function() {
//     const sectionIndex = this.getAttribute("data-section-index");
//     console.log(sectionIndex)
//     showSection(this);
//     updateNav(this);
//     removeBackSectionClass();
//     addBackSectionClass(sectionIndex)
// })

const navTogglerBtn = document.querySelector(".nav-toggler"),
    aside = document.querySelector(".aside");
navTogglerBtn.addEventListener("click", asideSectionTogglerBtn)

function asideSectionTogglerBtn() {
    aside.classList.toggle("open");
    navTogglerBtn.classList.toggle("open");
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.toggle("open");
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const selectedFileDiv = document.getElementById('selected-file');

    // Function to trigger prediction on page load
    function autoRunPrediction() {
        // Send POST request to run_prediction endpoint in Django
        fetch('/run_prediction/', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.predicted_class) {
                selectedFileDiv.innerHTML = `Predicted Class: ${data.predicted_class}`;
            } else {
                selectedFileDiv.textContent = 'Prediction failed.';
            }
        })
        .catch(error => {
            console.error('Error calling API:', error);
            selectedFileDiv.textContent = 'Error calling API.';
        });
    }

    // Run prediction automatically on page load
    autoRunPrediction();
});

// document.addEventListener("DOMContentLoaded", function() {
//     const audioUploadInput = document.getElementById('audio-upload');
//     const selectedFileDiv = document.getElementById('selected-file');
//     const playButton = document.getElementById('playButton');
//     const pauseButton = document.getElementById('pauseButton');
//     const audioPlayer = new Audio();
//     let audioLoaded = false;

//     // Handle file selection
//     audioUploadInput.addEventListener('change', function() {
//         const selectedFile = this.files[0];

//         if (selectedFile) {
//             selectedFileDiv.textContent = `Tệp chọn: ${selectedFile.name}`;
//             audioPlayer.src = URL.createObjectURL(selectedFile);
//             audioLoaded = true;
//             playButton.disabled = false;
//             pauseButton.disabled = false;
//         } else {
//             selectedFileDiv.textContent = 'Không có tệp nào được chọn.';
//             audioLoaded = false;
//             playButton.disabled = true;
//             pauseButton.disabled = true;
//         }
//     });

//     // Play button click event
//     playButton.addEventListener('click', function() {
//         if (audioLoaded) {
//             audioPlayer.play();
//         }
//     });

//     // Pause button click event
//     pauseButton.addEventListener('click', function() {
//         if (audioLoaded) {
//             audioPlayer.pause();
//         }
//     });
// });
