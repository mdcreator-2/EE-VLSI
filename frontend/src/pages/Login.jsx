import React from "react";
import Robo from "../assets/Gemini_Generated_Image_el2phoel2phoel2p (1)1.svg";
import Backbtn from "../assets/Backbtn.svg";
import LoginBg from "../assets/LoginPage(3).svg";

const Login = () => {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Background */}
      <img
        src={LoginBg}
        alt="Background"
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* Overlay */}
      <div className="absolute inset-0 bg-black/10"></div>

      {/* Content */}
      <div className="relative z-10 flex min-h-screen flex-col">
        
        {/* Back Button */}
        <div className="w-full">
          <img
            src={Backbtn}
            alt="Back"
            className="mt-5 ml-6 cursor-pointer"
          />
        </div>

        {/* Main Section */}
        <div className="flex flex-1 flex-col items-center justify-center gap-10 px-6 lg:flex-row lg:gap-24">
          
          {/* Robot Image */}
          <img
            src={Robo}
            alt="Robot"
            className="
              h-[45vh]
              object-contain
              sm:h-[55vh]
              md:h-[65vh]
              lg:h-[80vh]
            "
          />

          {/* Login Form */}
          <form className="flex flex-col items-center">
            <h2 className="mb-8 text-center text-3xl font-bold text-white">
              Log In
            </h2>

            <div
              className="
                w-full
                max-w-[450px]
                rounded-3xl
                border border-white/20
                bg-white/10
                p-6
                pt-10
                shadow-2xl
                backdrop-blur-xl
                sm:p-8
                sm:pt-12
                md:p-10
                md:pt-14
              "
            >
        <input
  type="text"
  placeholder="INSTITUTE EMAIL"
  className="
    w-full
    mb-4
    p-4
    rounded-xl
    bg-transparent
    border
    border-white/50
    text-white
    placeholder-white/70
    outline-none
    transition-all
    duration-300
    focus:border-white
    focus:shadow-[0_0_15px_rgba(255,255,255,0.4)]
    focus:-translate-y-1
  "
/>

           <input
  type="password"
  placeholder="PASSWORD"
  className="
    w-full
    mb-6
    p-4
    rounded-xl
    bg-transparent
    border
    border-white/50
    text-white
    placeholder-white/70
    outline-none
    transition-all
    duration-300
    focus:border-white
    focus:shadow-[0_0_15px_rgba(255,255,255,0.4)]
    focus:-translate-y-1
  "
/>
              <button
                type="submit"
                className="
                  w-full
                  rounded-xl
                  bg-white
                  py-4
                  font-semibold
                  text-black
                  transition-all
                  hover:scale-[1.02]
                "
              >
                LOG IN
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;