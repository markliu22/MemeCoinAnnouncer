import { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  const handleSubscribe = async () => {
    try {
      const response = await fetch('http://localhost:5001/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, phone }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Successfully subscribed!');
        setEmail('');
        setPhone('');
      } else {
        alert(`Subscription failed: ${data.error || 'Please try again.'}`);
      }
    } catch (error) {
      console.error('Error details:', error);
      alert('Error subscribing. Please try again later.');
    }
  };

  const handleUnsubscribe = async () => {
    try {
      const response = await fetch('http://localhost:5001/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, phone }),
      });
      
      if (response.ok) {
        alert('Successfully unsubscribed!');
        setEmail('');
        setPhone('');
      } else {
        alert('Unsubscription failed. Please try again.');
      }
    } catch (error) {
      alert('Error unsubscribing. Please try again later.');
    }
  };

  return (
    <div className="container">
      <h1>Welcome to MemeCoinAnnouncer! 🚀</h1>
      <p>Sign up to get notified (email, text, or both) when celebrities/influencers announce new tokens on X (Twitter)!</p>
      
      <div className="form">
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="tel"
          placeholder="Phone Number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <p className="input-help">
          For example,  +1 (123) 456-7890, please enter as: +11234567890
        </p>
        <div className="buttons">
          <button onClick={handleSubscribe}>Subscribe</button>
          <button onClick={handleUnsubscribe} className="unsubscribe">
            Unsubscribe
          </button>
        </div>
      </div>

      <div className="github-link">
        <p>
          Check out source code here:{' '}
          <a href="https://github.com/markliu22/MemeCoinAnnouncer" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </div>
    </div>
  );
}

export default App;