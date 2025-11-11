#!/bin/bash

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 164693826489.dkr.ecr.us-east-1.amazonaws.com

docker build --platform linux/amd64 --provenance false -t final_jpcb .

docker tag final_jpcb:latest 164693826489.dkr.ecr.us-east-1.amazonaws.com/final_jpcb:latest

docker push 164693826489.dkr.ecr.us-east-1.amazonaws.com/final_jpcb:latest