import './chatBot.css';
import { useEffect, useState } from 'react';
import { IoMdSend } from 'react-icons/io';
import { BiBot, BiUser } from 'react-icons/bi';

function Basic() {
  const [chat, setChat] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [botTyping, setBotTyping] = useState(false);

  useEffect(() => {
    const objDiv = document.getElementById('messageArea');
    objDiv.scrollTop = objDiv.scrollHeight;
  }, [chat]);

  const handleSubmit = (evt) => {
    evt.preventDefault();
    const name = "What-If Bot";
    const request_temp = { sender: "user", sender_id: name, msg: inputMessage };

    if (inputMessage !== "") {
      setChat(chat => [...chat, request_temp]);
      setBotTyping(true);
      setInputMessage('');
      rasaAPI(name, inputMessage);
    } else {
      window.alert("Please enter a valid message");
    }
  };

  const rasaAPI = async (name, msg) => {
    await fetch('http://localhost:5005/webhooks/rest/webhook', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'charset': 'UTF-8',
      },
      credentials: "same-origin",
      body: JSON.stringify({ "sender": name, "message": msg }),
    })
      .then(response => response.json())
      .then((response) => {
        if (response) {
          if (response.length === 1) {
            const temp = response[0];
            const recipient_id = temp["recipient_id"];
            const recipient_msg = temp["text"];

            const response_temp = { sender: "bot", recipient_id: recipient_id, msg: recipient_msg };
            setBotTyping(false);
            setChat(chat => [...chat, response_temp]);
          } else if (response.length > 1) {
            for (let i = 0; i < response.length; i++) {
              const temp = response[i];
              const recipient_id = temp["recipient_id"];
              const recipient_msg = temp["text"];

              const response_temp = { sender: "bot", recipient_id: recipient_id, msg: recipient_msg };
              setBotTyping(false);
              setChat(chat => [...chat, response_temp]);
            }
          }
        }
      });
  };

  const styleCard = {
    maxWidth: '50rem',
    border: '1px solid black',
    paddingLeft: '0px',
    paddingRight: '0px',
    borderRadius: '30px',
    boxShadow: '0 16px 20px 0 rgba(0,0,0,0.4)',
    margin: '20px auto'
  };

  const styleHeader = {
    height: '6rem',
    borderBottom: '1px solid black',
    borderRadius: '30px 30px 0px 0px',
    backgroundColor: '#4a90e2',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '10px'
  };

  const styleFooter = {
    borderTop: '1px solid black',
    borderRadius: '0px 0px 30px 30px',
    backgroundColor: '#4a90e2',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '10px'
  };

  const styleBody = {
    paddingTop: '10px',
    height: '35rem',
    overflowY: 'auto',
    overflowX: 'hidden',
    padding: '10px'
  };

  return (
    <div>
      <div className="container">
        <div className="row justify-content-center">
          <div className="card" style={styleCard}>
            <div className="cardHeader text-white" style={styleHeader}>
              <h1 style={{ marginBottom: '0px' }}>What-If Genbot</h1>
              {botTyping ? <h6>Bot Typing....</h6> : null}
            </div>
            <div className="cardBody" id="messageArea" style={styleBody}>
              <div className="row msgarea">
                {chat.map((user, key) => (
                  <div key={key}>
                    {user.sender === 'bot' ? (
                      <div className='msgalignstart'>
                        <BiBot className="botIcon" /><h5 className="botmsg">{user.msg}</h5>
                      </div>
                    ) : (
                      <div className='msgalignend'>
                        <h5 className="usermsg">{user.msg}</h5><BiUser className="userIcon" />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            <div className="cardFooter text-white" style={styleFooter}>
              <div className="row">
                <form style={{ display: 'flex', width: '100%' }} onSubmit={handleSubmit}>
                  <div className="col-10" style={{ paddingRight: '0px' }}>
                    <input onChange={e => setInputMessage(e.target.value)} value={inputMessage} type="text" className="msginp" placeholder="Type a message..." />
                  </div>
                  <div className="col-2 cola">
                    <button type="submit" className="circleBtn"><IoMdSend className="sendBtn" /></button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Basic;