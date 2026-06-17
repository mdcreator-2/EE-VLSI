import React from "react";
import { Link } from "react-router-dom";

import HeroBg from "../assets/Hero.svg";
import MainLogo from "../assets/MainLogo.svg";
import RoboSvg from "../assets/Robo.svg";

const buttons = [
  { name: "VAULT", path: "/vault" },
  { name: "CHRONICLES", path: "/chronicles" },
  { name: "DIRECTORY", path: "/directory" },
  { name: "FORGE", path: "/forge" },
];

const Hero = () => {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Background */}
      <img
        src={HeroBg}
        alt="Background"
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/20"></div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Logo */}
        <img
          src={MainLogo}
          alt="Logo"
          className="
            mt-10
            w-[260px]

            sm:w-[320px]

            md:w-[420px]
          "
        />

        {/* Buttons */}
        <div
          className="
            mt-8

            flex
            flex-wrap

            justify-center

            gap-5

            md:gap-10
          "
        >
          {buttons.map((btn) => (
            <Link
              key={btn.name}
              to={btn.path}
              className="
                h-14
                w-40

                rounded-full

                border-[3px]
                border-white

                bg-[#240000]/50

                text-sm
                font-semibold

                tracking-wider
                text-white

                transition-all
                duration-300

                hover:scale-105
                hover:bg-white
                hover:text-black

                flex
                items-center
                justify-center
              "
            >
              {btn.name}
            </Link>
          ))}
        </div>

        {/* Robot */}
        <img
          src={RoboSvg}
          alt="Robot"
          className="
            mt-12

            w-[260px]

            sm:w-[330px]

            md:w-[420px]

            lg:w-[480px]
          "
        />
      </div>
    </div>
  );
};

export default Hero;