import React, { useState } from "react";
import Robo2 from "../assets/Gemini_Generated_Image_l53ymbl53ymbl53y (1) 1.svg";
import Backbtn from "../assets/Backbtn.svg";
import LoginBg from "../assets/LoginPage(3).svg";
import SignUpLogo from "../assets/Union.svg";

const SignUp = () => {
  const [profileImage, setProfileImage] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (file) {
      setProfileImage(URL.createObjectURL(file));
    }
  };

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
          {/* Left Side */}
          <div className="flex flex-col items-center justify-center mb-8">
            <h2 className="mb-8 text-center text-3xl font-bold text-white">
              Sign Up
            </h2>

            <img
              src={Robo2}
              alt="Robot"
              className="
                h-[45vh]
                object-contain
                sm:h-[55vh]
                md:h-[65vh]
                lg:h-[70vh]
              "
            />
          </div>

          {/* Right Side */}
          <div>
            <form className="flex flex-col items-center mb-8
            ">
              {/* Upload Profile Picture */}
    <div
  className="
    flex
    flex-col
    items-center
    justify-center
    w-[300px]
    h-[160px]
    rounded-[100px]
    bg-white/10
    backdrop-blur-md
    shadow-[0_10px_30px_rgba(0,0,0,0.35)]
    border
    border-white/10
    px-6
    py-4
    mb-[15px]
  "
>
  <div
    className="image-se relative h-32 w-32 cursor-pointer overflow-hidden rounded-full"
    onClick={() => document.querySelector('input[type="file"]').click()}
  >
    <input
      type="file"
      accept="image/*"
      onChange={handleImageChange}
      className="hidden"
    />

    {profileImage ? (
      <img
        src={profileImage}
        alt="Profile Preview"
        className="h-full w-full object-cover"
      />
    ) : (
      <img
        src={SignUpLogo}
        alt="Upload Profile"
        className="h-full w-full object-contain"
      />
    )}
  </div>

  <span className="mt-2 text-xs text-white tracking-wide">
    UPLOAD YOUR PROFILE PICTURE
  </span>
</div>
              <div
                className="
                  w-full
                  max-w-[450px]
                  rounded-3xl
                  border border-white/10
                  bg-white/5
                  p-6
                  pt-10
                  shadow-2xl
                  backdrop-blur-[2px]
                  sm:p-8
                  sm:pt-12
                  md:p-10
                  md:pt-14
                "
              >
                <input
                  type="text"
                  placeholder="NAME"
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
                  type="email"
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
                    text-[#851616]
                    transition-all
                    hover:scale-[1.02]
                  "
                >
                  SUBMIT
                </button>

                <button
                  type="button"
                  className="
                    w-full
                    py-4
                    font-semibold
                    text-white
                    transition-all
                    hover:scale-[1.02]
                  "
                >
                  LOG IN (EXISTING USER)
                </button>
              </div>


            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignUp;