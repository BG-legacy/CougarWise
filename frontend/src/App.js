import React from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./App.css";
import { PieChart, Pie, Cell, Tooltip, Legend } from "recharts";

/* Import images */
import FinancialPlannerImg from "./F.jpg";
import W_BG from "./W.webp";
import D_BG from "./BL.jpg";
import F_BG from "./FinancialPlanning_BG.jpg"
import B_BG from "./DarkB.jpg"
import FB_2 from "./FP2_BG.jpg"

// Home Page Component
function Home() {
  const navigate = useNavigate();

  return (
    <div className="App">
      <header className="App-header">
        {/* Background Image */}
        <img src={W_BG} alt="Background"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "100%",
            height: "100%",
            opacity: 0.9,
            zIndex: 0,
          }}
        />

        {/* Financial Planner Image */}
        <img src={FinancialPlannerImg} alt="Financial Planner"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -250px)",
            width: "800px",
            height: "300px",
            opacity: 0.9,
            zIndex: 1,
          }}
        />

        {/* Left White Box */}
        <img src={W_BG} alt="Left White Box"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-750px, -250px)",
            width: "300px",
            height: "400px",
            opacity: 0.9,
            zIndex: 2,
          }}
        />

        {/* Dark Borders */}
        <img src={D_BG} alt="Left Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-450px, -450px)",
            width: "50px",
            height: "800px",
            opacity: 0.9,
            zIndex: 2,
          }}
        />

        <img src={D_BG} alt="Right Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(400px, -450px)",
            width: "50px",
            height: "800px",
            opacity: 0.9,
            zIndex: 2,
          }}
        />

        {/* Title and Welcome Text */}
        <h1 style={{position: "absolute", top: "-50px", fontSize: "50px", color: "Black", zIndex: 1, }}>
        Cougarwise </h1>

        <p style={{position: "absolute", top: "80px", color: "Black", zIndex: 1,}}>
        Welcome to your financial planner! </p>

        {/* "Who Are We?" Section */}
        <h2 style={{position: "absolute", color: "Black", transform: "translate(-600px, -300px)", fontSize: "48px", zIndex: 2, }}>
          Who are We?
        </h2>

        <p style={{position: "absolute", color: "Black", transform: "translate(-600px, -100px)", width: "300px", fontSize: "20px", 
        zIndex: 2,}}>
          Cougarwise is your personal financial planner, helping you track expenses, set budgets, and reach your goals.
          Our features include: <br /> 1. Smart budgeting and Goal tracking <br /> 2. Personalized AI financial insights
          <br /> 3. User-Friendly Dashboard and Reports <br /> 4. AI chatbot for financial advice
        </p>

        {/* Navigation Buttons */}
        <button style={{ transform: "translate(-50%, -245px)" }} onClick={() => navigate("/login")}> 
          Click here to Login </button>
        <button style={{ transform: "translate(70px, -266px)" }} onClick={() => navigate("/signup")}>
          Click Here to Signup </button>

        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
          zIndex="2"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

// Signup Page Component
function SignupPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    email: "",
    password: "",
    zipcode: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Firstname: ${formData.firstname}\nLastname: ${formData.lastname}\nEmail: ${formData.email}\nPassword: ${formData.password}\nZipcode: ${formData.zipcode}`);
  };
  

  return (
    <div className="App">
      <header className="App-header">
        <h1 
        style = {{
          position: "absolute",
          transform: "translate(0px, -300px)",
          zIndex: 2,
        }}>
        Sign Up for Cougarwise!</h1>
        <p style = {{zIndex: 2, fontSize: "40px", position: "absolute", width: "600px", transform: "translate(-400px, -100px)"}}>
        Cougarwise is equipped with the latest technologies to ensure effective, quick, and efficient financial
        planning.</p>

        <p style = {{zIndex: 2, fontSize: "28px", position: "absolute", width: "600px", transform: "translate(-400px, 150px)"}}>
        With the use of high end Artificial Intelligence, Cougarwise is designed to give you the best financial advice possible
        to help you reduce spending, increase your savings, escape debt and even invest!
        </p>
        {/* Navigation Buttons */}
        <button style = {{zIndex: 2, transform: "translate(-400px, -280px", height: "40px"}} onClick={() => navigate("/")}>Go Back to Home</button>
        <button style = {{zIndex: 2, transform: "translate(400px, -315px", height: "40px"}} onClick={() => navigate("/login")}>Go to Login Page</button>

        {/*Sign-up form*/}

        <form onSubmit={handleSubmit}
        style = {{
          position: "absolute",
          top: "50%",
          left: "50%",
            transform: "translate(-50%, -50%)",
            zIndex: 2,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}>
            <input type = "firstname" name ="firstname" value = {formData.firstname} onChange={handleChange}
            placeholder="Enter your firstname" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

            <input type = "lastname" name ="lastname" value = {formData.lastname} onChange={handleChange}
            placeholder="Enter your lastname" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

            <input type = "email" name ="email" value = {formData.email} onChange={handleChange}
            placeholder="Enter your email" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>    

            <input type = "password" name ="password" value = {formData.password} onChange={handleChange}
            placeholder="Enter your password" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

            <input type = "zipcode" name ="zipcode" value = {formData.zipcode} onChange={handleChange}
            placeholder="Enter your zipcode" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>
            <button type="submit" style={{ padding: "10px 20px", fontSize: "16px", transform: "translate(250px, 0px" }}>
            Sign Up
            </button>
          </form>

        {/* Images */}

        <img src={B_BG} alt="Bluebackground img"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "100%",
            height: "100%",
            opacity: 0.5,
            zIndex: 1,
          }}/>

        <img src={F_BG} alt="Financial planner img"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "100%",
            height: "100%",
            opacity: 0.9,
            zIndex: 0,
          }}/>

        <img src={D_BG} alt="Top Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -250px)",
            width: "100%",
            height: "50px",
            opacity: 0.9,
            zIndex: 2,
          }}/>


      </header>
    </div>
  );
}

// Login Page Component
function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    password: "",
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Firstname: ${formData.firstname}\nLastname: ${formData.lastname}\nPassword: ${formData.password}\n`);
  };
  

  return (
    <div className="App">
      <header className="App-header">
        <h1 
        style = {{
          position: "absolute",
          transform: "translate(0px, -300px)",
          zIndex: 2,
        }}>
        Login to Cougarwise </h1>

        <p style = {{position: "absolute", zIndex: 2, fontSize: 40, width: 500, transform: "translate(-500px, 50px)"}}>
          Welcome back, log back in to continue receiving Financial Advice to continue furthering your financial progress.</p>
        {/* Navigation Buttons */}
        <button style = {{position: "absolute", zIndex: 2, transform: "translate(350px, -300px", height: "40px"}} onClick={() => navigate("/")}>Go Back to Home</button>
        <button style = {{position: "absolute", zIndex: 2, transform: "translate(-350px, -300px", height: "40px"}} onClick={() => navigate("/signup")}>Go to Signup Page</button>
      
                {/*Sign-up form*/}

                <form onSubmit={handleSubmit}
        style = {{
          position: "absolute",
          top: "50%",
          left: "50%",
            transform: "translate(-50%, -50%)",
            zIndex: 2,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}>
            <input type = "firstname" name ="firstname" value = {formData.firstname} onChange={handleChange}
            placeholder="Enter your firstname" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

            <input type = "lastname" name ="lastname" value = {formData.lastname} onChange={handleChange}
            placeholder="Enter your lastname" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

            <input type = "password" name ="password" value = {formData.password} onChange={handleChange}
            placeholder="Enter your password" required style = {{marginBottom: "10px", padding: "10px", fontSize: "16px",
            width: "300px", transform: "translate(250px, 0px" }}/>

      
            <button type="submit" style={{ padding: "10px 20px", fontSize: "16px", transform: "translate(250px, 0px" }}
            onClick={() => navigate("/profile")}>
            Login
            </button>
          </form>

        <img src={D_BG} alt="Top Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -250px)",
            width: "100%",
            height: "50px",
            opacity: 0.9,
            zIndex: 2,
          }}/>

          <img src={FB_2} alt="background"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: "100%",
            height: "100%",
            opacity: 0.5,
            zIndex: 1,
          }}
        />
          
      </header>
      
    </div>
  );
}

function ProfilePage() {
  const navigate = useNavigate();
  

  return (
    <div className="App">
      <header className="App-header">
      <h1 style = {{ position: "absolute", transform: "translate(0px, -300px)", zIndex: 2}}>
      View Your Profile</h1>
      <button style = {{position: "absolute", zIndex: 2, transform: "translate(-350px, -300px)", height: "40px"}} 
      onClick={() => navigate("/")}> Logout</button>
      <button style = {{position: "absolute", zIndex: 2, transform: "translate(350px, -300px)", height: "40px"}} 
      onClick={() => navigate("/dashboard")}> View Dashboard</button>
      <button style = {{position: "absolute", zIndex: 2, transform: "translate(500px, -300px)", height: "40px"}} 
      onClick={() => navigate("/insights")}> View Insights</button>

          {/*images */}

          <img src={D_BG} alt="Top Border" style={{ position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -250px)", width: "100%", height: "50px", opacity: 0.9,
            zIndex: 2}}/>

          <img src={W_BG} alt = "White" style={{position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -200px)", width: "100%", height: "552px", opacity: 0.9,
            zIndex: 1}}/>

          <img src={W_BG} alt = "White" style={{position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -170px)", width: "800px", height: "500px", opacity: 0.9,
            zIndex: 3}}/>

          {/* text boxes */}

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 4, transform: "translate(-400px, -200px)",
            color: "black", }}> Firstname</p>

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 4, transform: "translate(-400px, -170px)",
            color: "black", }}> Lastname</p>

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 4, transform: "translate(-400px, -140px)",
            color: "black", }}> Zipcode</p>

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 4, transform: "translate(-400px, -110px)",
            color: "black", }}> Email</p>
    

      </header>
    </div>
  )

}

function DashboardPage() {
  const navigate = useNavigate();
  const data = [
    { name: "Shoping", value: 52 },
    { name: "Sport", value: 16 },
    { name: "Food", value: 12 },
    { name: "Clothes", value: 12 },
    { name: "Others", value: 8 },
  ];

  const COLORS = ["#7166F9", "#5CC8C3", "#FFC641", "#07156A", "#E5E4F1"];


  return (
    <div className="App">
      <header className="App-header">
        <h1 style={{ position: "absolute", transform: "translate(0px, -300px)", zIndex: 2 }}>
          View Your Dashboard
        </h1>
        <button style={{ position: "absolute", zIndex: 2, transform: "translate(-350px, -300px)", height: "40px" }} 
          onClick={() => navigate("/")}> Logout</button>
        <button style={{ position: "absolute", zIndex: 2, transform: "translate(350px, -300px)", height: "40px" }} 
          onClick={() => navigate("/profile")}> View Profile</button>

     
      

      {/*Images*/}
          <img src={D_BG} alt="Top Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -250px)",
            width: "100%",
            height: "50px",
            opacity: 0.9,
            zIndex: 2,
          }}/>

          
          <img src={W_BG} alt = "White" style={{position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -200px)", width: "100%", height: "552px", opacity: 0.9,
            zIndex: 1}}/>

            <img src={W_BG} alt = "White" style={{position: "absolute", top: "50%", left: "50%",
            transform: "translate(-600px, -100px)", width: "400px", height: "400px", opacity: 0.9,
            zIndex: 2}}/>

          {/*Text boxes*/}

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 3, transform: "translate(-800px, -220px)",
            color: "black", }}> Welcome to your dashboard, here you can see your spending information </p>

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 3, transform: "translate(-600px, -130px)",
            color: "black", }}> Bank information </p>

          <p style = {{position: "absolute", top:"50%", left: "50%", zIndex: 3, transform: "translate(-600px, -100px)",
            color: "black", }}> Bank information </p>
    
      </header>
    </div>
  );
}

function InsightsPage() {
  const navigate = useNavigate();
  const [isChatOpen, setIsChatOpen] = useState(false);
  const toggleChat = () => setIsChatOpen(!isChatOpen);

  return (
    <div className="App">
      <header className="App-header">
      <h1 
        style = {{
          position: "absolute",
          transform: "translate(0px, -300px)",
          zIndex: 2,
        }}>
      View Your Insights</h1>
      <button style = {{position: "absolute", zIndex: 2, transform: "translate(-350px, -300px", height: "40px"}} 
      onClick={() => navigate("/")}> Logout</button>
      <button style = {{position: "absolute", zIndex: 2, transform: "translate(350px, -300px", height: "40px"}} 
      onClick={() => navigate("/profile")}> View profile</button>
      <button style={{ position: "absolute", zIndex: 2, transform: "translate(450px, -300px)", height: "40px" }} 
      onClick={toggleChat}> Chatbot</button>
      
          <img src={D_BG} alt="Top Border"
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -250px)",
            width: "100%",
            height: "50px",
            opacity: 0.9,
            zIndex: 2,
          }}/>

        {/* Chatbot UI */}
        {isChatOpen && (
          <div className="chat-window">
            <div className="chat-header">
              <span>Chat</span>
              <button className="close-btn" onClick={toggleChat}>X</button>
            </div>
            <div className="chat-body">
              <p>Hello! This is Cougarwise's automated Agent designed to help you plan your decisions.</p>
              <ul>
                <li>Ask a Question</li>
              </ul>
            </div>
          </div>
        )}      
      </header>
    </div>
  )

}



// App Component with Routing
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/insights" element={<InsightsPage />} />
      </Routes>
    </Router>
  );
}

export default App;