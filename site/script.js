var app = new Vue({
    el: '#app',
    data: {
        speakers: [],
        text: '',
        fileName: '',
        botCreated: false,
        selectedSpeakerData_: "",
        botToken: ""
    },

    computed: {
        selectedSpeaker: {
            get: function () {
                if (this.selectedSpeakerData_ !== "") {
                    return this.selectedSpeakerData_;
                }
                if (this.speakers.length ===0){
                    return "";
                }
                return this.speakers[0];
            },
            set: function (newValue) {
                this.selectedSpeakerData_ = newValue;
            }
        }
    },
    methods: {
        loadFileAsText: function (event) {
            this.botCreated=false;
            var fileToLoad = event.target.files[0];
            this.fileName = fileToLoad.name;
            var fileReader = new FileReader();
            fileReader.onload = function (fileLoadedEvent) {
                this.text = fileLoadedEvent.target.result;
                var speakers = parseSpeakers(this.text);
                app.speakers = Array.from(speakers);
                if (speakers.size === 0) {
                    alert("We were not able to parse the uploaded file. make sure the file is an exported Whatsapp chat or contact support");
                    throw 42;
                }
            };
            fileReader.readAsText(fileToLoad, "UTF-8");
        },
        sendText: function () {
            var url = 'https://l7f691qjn6.execute-api.eu-west-2.amazonaws.com/production';
            var data = {
                token: this.botToken,
                text: this.text,
                speaker: this.selectedSpeaker
            };
            var headers = {"Content-Type": "application/json; charset=UTF-8"};
            var params = {headers: headers, body: JSON.stringify(data), method: "POST"};
            fetch(url, params).then(data => {
                return data
            }).then(res => console.log(res)).catch(error => {
                ///alert("We could not create your bot. make sure the token is correct or contact support")
                console.log(error)
            }).then(function () {
                app.speakers = [];
                app.text = '';
                app.selectedSpeaker="";
                app.botToken = '';
                app.botCreated=true;
            })
        }
    }
});

function parseSpeakers(text) {
    var TIME = /[?\d{1,2}[/.]\d{1,2}[/.]\d{2,4}, \d{1,2}:\d{2}(?::\d{1,2})?(?: (?:AM|PM))?]?(?: -)? /i;
    var SPEAKER_MESSAGE = /([^:]*): (.*)/i;
    var sender_messages = text.split(TIME);
    var speakers = new Set();
    for (var i = sender_messages.length - 1; i >= 0; i--) {
        var speaker_message = sender_messages[i].match(SPEAKER_MESSAGE);
        if ((speaker_message) && (speaker_message[1] != null)) {
            speakers.add(speaker_message[1]);
        }
    }
    return speakers;
}

