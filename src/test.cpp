#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "iostream"

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  
  geometry_msgs::msg::Twist controlVel;

  controlVel.linear.x = 0.3;
  controlVel.linear.y = 0;
  controlVel.linear.z = 0;
  controlVel.angular.x = 0;
  controlVel.angular.y = 0;
  controlVel.angular.z = 1;

  // Create a node by calling the constructor of rcl::cpp Node class
  auto testNode = rclcpp::Node::make_shared("test_node");

  // Function returns a shared pointed to the created publisher
  auto publisher = testNode->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 5);
  rclcpp::Rate controlRate(1000);

  // While loop to keep the node running and publishing messages until the node is shutdown
  while (rclcpp::ok())
  {
    publisher->publish(controlVel);
    rclcpp::spin_some(testNode); // creates a default single-threaded executor and execute any immediately available
    controlRate.sleep();
  }

  rclcpp::shutdown();

  return 0;
}
