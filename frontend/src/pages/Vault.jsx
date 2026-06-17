import React from "react";
import { Link } from "react-router-dom";

import VaultBg from "../assets/Vault.svg";
import Backbtn from "../assets/Backbtn.svg";
import TextImg from "../assets/TheVault.svg";

import UploadResoBtn from "../assets/Frame31.svg";
import ViewResoBtn from "../assets/Frame32.svg";

const Vault = () => {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">

      {/* Background */}
      <img
        src={VaultBg}
        alt=""
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* Content */}
      <div className="relative z-10 flex min-h-screen flex-col">

        {/* Back Button */}
        <div className="w-full">
          <Link to="/" className="inline-block">
            <img
              src={Backbtn}
              alt="Back"
              className="mt-5 ml-6 cursor-pointer"
            />
          </Link>
        </div>

        {/* Title */}
        <img
          src={TextImg}
          alt="The Vault"
          className="
            mx-auto
            mt-18
            w-[340px]

            md:w-[380px]
          "
        />

        {/* Buttons */}
        <div
          className="
            mt-20
            flex
            w-full

            flex-col
            items-center
            justify-center

            gap-8

            lg:flex-row
            lg:gap-24
          "
        >

          {/* Upload */}
          <button
            className="
              relative
              cursor-pointer

              transition-all
              duration-300
              ease-out

              hover:scale-102
              hover:-translate-y-2

              active:scale-95
            "
          >
            <img
              src={UploadResoBtn}
              alt="Upload Resources"
              className="
                w-[180px]

                md:w-[230px]

                drop-shadow-lg
                transition-all
                duration-300

                hover:drop-shadow-2xl
              "
            />
          </button>

          {/* View */}
          <button
            className="
              relative
              cursor-pointer

              transition-all
              duration-300
              ease-out

              hover:scale-102
              hover:-translate-y-2

              active:scale-95
            "
          >
            <img
              src={ViewResoBtn}
              alt="View Resources"
              className="
                w-[180px]

                md:w-[230px]

                drop-shadow-lg
                transition-all
                duration-300

                hover:drop-shadow-2xl
              "
            />
          </button>

        </div>

      </div>

    </div>
  );
};

export default Vault;