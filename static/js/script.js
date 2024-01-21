class General {
  static setErrorText(message) {
    var errorText = document.querySelector(".error");
    errorText.innerText = message;
  }
}

class CoursePage {
  static createCourseSetShowing(showing) {
    var createCoursePlus = document.querySelector(".course-card.add");
    var createCourseCard = document.querySelector(".course-card.create");
    createCoursePlus.classList[showing ? "add" : "remove"]("toggled");
    createCourseCard.classList[showing ? "add" : "remove"]("toggled");
    if (!showing) {
      var addedStudentEmailsText = document.querySelector(
        "p.added-student-emails"
      );
      addedStudentEmailsText.innerHTML = "";
    }
  }

  static addStudent() {
    var addedStudentEmailsText = document.querySelector(
      "p.added-student-emails"
    );
    var addStudentInput = document.querySelector("input.add-student");
    if (!addStudentInput.checkValidity() || addStudentInput.value == "") {
      return;
    }
    var newStudentSpan = document.createElement("span");
    newStudentSpan.innerText = addStudentInput.value;
    addedStudentEmailsText.appendChild(newStudentSpan);
    newStudentSpan.addEventListener("click", (ev) => {
      ev.target.remove();
    });
    addStudentInput.value = "";
  }

  static createCourse() {
    var data = {
      name: "",
      subject: "",
      students: [],
    };

    var courseNameInput = document.querySelector("input.course-name");
    data.name = courseNameInput.value;

    var courseSubjectInput = document.querySelector("select.course-subject");
    data.subject = courseSubjectInput.value;

    var addedStudentEmailsText = document.querySelector(
      "p.added-student-emails"
    );
    var studentEmailElems = addedStudentEmailsText.querySelectorAll("span");
    for (var e = 0; e < studentEmailElems.length; e++) {
      data.students.push(studentEmailElems.item(e).innerText);
    }

    if (!data.name || data.subject == "0") {
      General.setErrorText("Enter all fields");
      return;
    }

    var createCourseBtn = document.querySelector(
      ".course-card.create .button.submit"
    );
    createCourseBtn.classList.add("disabled");

    fetch("/course/create", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((res) => res.json())
      .then((json) => console.log(json))
      .catch((reason) => console.log(reason))
      .finally(() => {
        location.reload();
      });
  }

  static joinCourse() {
    var data = {
      course_id: "",
    };

    var courseIDInput = document.querySelector("input.course-id");
    data.course_id = courseIDInput.value;

    if (!data.course_id || !courseIDInput.checkValidity()) {
      General.setErrorText("Enter a 5-character code");
      return;
    }

    var joinCourseBtn = document.querySelector(
      ".course-card.join .join-class-btn"
    );
    joinCourseBtn.classList.add("disabled");

    fetch("/course/join", {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-type": "application/json; charset=UTF-8",
      },
    })
      .then((res) => res.json())
      .then((json) => console.log(json))
      .catch((reason) => console.log(reason))
      .finally(() => {
        location.reload();
      });
  }
}

class LessonPage {
  static createLesson() {
    var nameInput = document.querySelector("input.course-name-input");
    var videoInput = document.querySelector("input.video-input");
    var courseInput = document.querySelector("input.course-id-input");
    var files = videoInput.files;
    if (!files.length) {
      General.setErrorText("Upload a video and enter lesson name");
      return;
    }
    var formData = new FormData();
    var video = files[0];
    formData.append("name", nameInput.value);
    formData.append("lessonvideo", video);
    formData.append("course_id", courseInput.value);

    var uploadBtn = document.querySelector(".upload-btn");
    uploadBtn.classList.add("disabled");

    fetch("/lesson/create", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
      })
      .finally(() => {
        location = "/course/" + courseInput.value;
      });
  }
}

addEventListener("DOMContentLoaded", () => {
  var addStudentInput = document.querySelector("input.add-student");
  addStudentInput.addEventListener("keyup", (e) => {
    if (e.key == "Enter") {
      CoursePage.addStudent();
    }
  });
});

const ctrl = {
    "A": ["a", 0],
    "B": ["b", 0],
    "C": ["c", 0],
    "D": ["d", 0],

    "E": ["a", 1],
    "F": ["b", 1],
    "G": ["c", 1],
    "H": ["d", 1],

    "I": ["a", -1],
    "J": ["b", -1],
    "K": ["c", -1],
    "L": ["d", -1],
}

function serialInit() {
    async function connect() {
        try {
        const port = await navigator.serial.requestPort();
        await port.open({ baudRate: 9600 });
        document.getElementById("status").textContent = "Status: Connected";

        port.onReceive = async (event) => {
            const data = event.data;
            console.log("Received:", data);
        };

        // Continuously check for serial input:
        const reader = port.readable.getReader();
        setInterval(() => {
            if (port.readable) {
            reader.read().then(({ value, done }) => {
                if (value) {
                var letterRecieved = String.fromCharCode.apply(null, value);
                window.par1;
                window.par2;
                switch (letterRecieved) {
                    case "A":
                        window.par1 = 'a';
                        window.par2 = 0;
                        break;
                    case "B":
                        window.par1 = 'b';
                        window.par2 = 0;
                        break;
                    case "C":
                        window.par1 = 'c';
                        window.par2 = 0;
                        break;
                    case "D":
                        window.par1 = 'd';
                        window.par2 = 0;
                        break;

                    case "L":
                        window.par1 = 'd';
                        window.par2 = -1;
                        break;
                    case "F":
                        window.par1 = 'b';
                        window.par2 = 0;
                        break;
                    case "G":
                        window.par1 = 'c';
                        window.par2 = 0;
                        break;
                    case "H":
                        window.par1 = 'd';
                        window.par2 = 0;
                        break;


                    default:
                        break;
                }
                console.log(window.par1, window.par2);
                QuizControl.affectQuestion(window.par1, window.par2);
                }
                if (!done) {
                }
            });
            }
            else {
                console.log("not readable");
            }
        }, 100);
        } catch (error) {
        console.error("Error connecting:", error);
        document.getElementById("status").textContent = "Status: Error";
        }
    }

    document.getElementById("connectButton").addEventListener("click", connect);
}

var quizChoices = {};
var quizCurrentQuestion = 0;
var quizState = 0; // 1 ongoing, 2 done

class QuizControl {
    // action: 1 is recover, 0 is answer, -1 is eliminate
    static affectQuestion(option, action) {
        var qContainer = document.querySelector(".quiz-container");
        var currentQ = qContainer.querySelectorAll(".quiz-question").item(quizCurrentQuestion-1);
        var answerContainer = currentQ.querySelector(".answer-choice-container");
        var toNum = "abcd".indexOf(option) + 1;
        if (toNum) {
            option = toNum;
        }
        var chosenAnswer = answerContainer.querySelectorAll(".answer-choice").item(option-1);
        switch (action) {
            case 1:
                chosenAnswer.classList.remove("eliminated");
                break;

            case -1:
                chosenAnswer.classList.add("eliminated");
                chosenAnswer.classList.remove("chosen");
                break;

            default:
                quizChoices[quizCurrentQuestion] = chosenAnswer.innerText.trim();
                chosenAnswer.classList.add("chosen");
                chosenAnswer.classList.remove("eliminated");
                QuizControl.nextQuestion();
                break;
        }
    }

    static nextQuestion() {
        quizCurrentQuestion++;
        var qContainer = document.querySelector(".quiz-container");
        var oldQ = qContainer.querySelectorAll(".quiz-question").item(quizCurrentQuestion-2);
        var currentQ = qContainer.querySelectorAll(".quiz-question").item(quizCurrentQuestion-1);
        if (!currentQ) {
            QuizControl.finishQuiz();
            return;
        }
        var answerContainer = currentQ.querySelector(".answer-choice-container");

        if (quizCurrentQuestion > 1) {
            oldQ.classList.remove("current");
        }
        else {
            var startBtn = document.querySelector(".quizStartBtn");
            startBtn.classList.add("disabled");
            quizState = 1;
        }
        currentQ.classList.add("current");
    }

    static finishQuiz() {
        var quizResultText = document.querySelector(".quiz-result");
        quizResultText.innerHTML = "YOUR ANSWERS: " + Object.values(quizChoices).join(", ");
        quizState = 2;
    }

    static submitQuiz() {
        if (quizState != 2) {
            return;
        }
    }
}