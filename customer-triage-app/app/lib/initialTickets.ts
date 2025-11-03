import { Ticket } from "../components/types";

export const initialTickets: Ticket[] = [
  {
    id: 1,
    text: "I tried to pay my bill online but your site kept giving error 500, and the chatbot was no help at all. This is the third time this month!",
    stage: "uploaded",
  },
  {
    id: 2,
    text: "Just wanted to let you know the delivery was late but it arrived safely. Great packaging! Thanks for the excellent service.",
    stage: "uploaded",
  },
  {
    id: 3,
    text: "Reset my password 3 times, still can't get access. Please fix this ASAP or I'll move to another provider! This is unacceptable and I'm considering legal action.",
    stage: "uploaded",
  },
  {
    id: 4,
    text: "How do I set up automatic billing? I couldn't find the option in my account settings. Would appreciate some help with this.",
    stage: "uploaded",
  },
  {
    id: 5,
    text: "I was charged twice for the same order (#12345). I need a refund immediately! My bank statement shows duplicate charges from your company.",
    stage: "uploaded",
  },
  {
    id: 6,
    text: "Your product exceeded my expectations! The quality is amazing and shipping was super fast. Will definitely order again and recommend to friends!",
    stage: "uploaded",
  },
  {
    id: 7,
    text: "My package tracking says it was delivered yesterday but I never received it. Where is my order? I've been waiting for 2 weeks now.",
    stage: "uploaded",
  },
  {
    id: 8,
    text: "The mobile app keeps crashing whenever I try to view my order history. Tried reinstalling but the problem persists. Can you help?",
    stage: "uploaded",
  },
];
