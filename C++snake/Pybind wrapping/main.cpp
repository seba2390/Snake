// STL includes
#include <tuple>
#include <deque>
#include <iostream>
#include <array> // for std::array
#include <cassert> // for assertions
#include <cstdlib>

// Pybind include
#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>
#include <pybind11/stl.h>
#include <boost/circular_buffer.hpp>

int random_int(const int& low,
               const int& high){
    assert(low < high);
    return rand() % (high-1) + low;
}

class FakeRect
{
private:
    int height;
    int width;
    std::array<int,2> size;
public:
    int _centerx, _centery, _left, _right, _top, _bottom;

    // Standard C-tor
    FakeRect(){
        this-> height = 0;
        this-> width = 0;
        this->_centerx = 0;
        this->_centery = 0;
        this->_left = 0;
        this->_right = 0;
        this->_top = 0;
        this->_bottom = 0;
        this->size[0] = 0; this->size[1] = 0;
    };

    // Parametrized C-tor
    FakeRect(
            const int& height,
            const int& width,
            int centerx = 0,
            int centery = 0,
            int left = 0,
            int right = 0,
            int top = 0,
            int bottom = 0)
    {
        assert(height % 2 == 0);
        assert(width == height);

        // Private const definitions.
        this->height = height;
        this->width = width;
        this->size[0] = this->height; this->size[1] = this->width,

                // Public non-const definitions.
                this->_centerx = centerx;
        this->_centery = centery;
        this->_left = left;
        this->_right = right;
        this->_top = top;
        this->_bottom = bottom;
    }

    void move(const int& vx,
              const int& vy)
    {
        set_left(get_left()+vx);
        set_bottom(get_bottom()+vy);
    }


    // Method for cloning instance of class
    FakeRect clone() const
    {
        return FakeRect(this->height, this->width,
                        this->_centerx, this->_centery,
                        this->_left, this->_right,
                        this->_top, this->_bottom);
    }

    // Setters and Getters that dynamically updates attributes
    int get_centerx() const {return this->_centerx;}
    void set_centerx(int centerx)
    {
        this->_centerx = centerx;
        this->_left = this->_centerx-(int)(this->width/2);
        this->_right = this->_centerx+(int)(this->width/2);
    }

    int get_centery() const{return this->_centery;}
    void set_centery(int centery)
    {
        this->_centery = centery;
        this->_top = this->_centery-(int)(this->height/2);
        this->_bottom = this->_centery+(int)(this->height/2);
    }

    int get_left() const{return this->_left;}
    void set_left(int left)
    {
        this->_left = left;
        this->_right = this->_left+this->width;
        this->_centerx = this->_left+(int)(this->width/2);
    }

    int get_right() const{return this->_right;}
    void set_right(int right)
    {
        this->_right = right;
        this->_left = this->_right-this->width;
        this->_centerx = this->_right-(int)(this->width/2);
    }

    int get_top() const{return this->_top;}
    void set_top(int top)
    {
        this->_top = top;
        this->_bottom = this->_top+this->height;
        this->_centery = this->_top+(int)(this->height/2);
    }

    int get_bottom() const{return this->_bottom;}
    void set_bottom(int bottom)
    {
        this->_bottom = bottom;
        this->_top = this->_bottom-this->height;
        this->_centery = this->_bottom-(int)(this->height/2);
    }

    std::array<int,2> get_size(){return this->size;}
};




class Block
{
public:

    FakeRect rect;
    std::string direction;

    // Standard un-parametrized C-tor
    Block()
    {
        this->direction = "NaN";
        this->rect = FakeRect(0,0,
                                    0,0,
                                    0,0,
                                    0,0);
    };

    explicit Block(const FakeRect& rect,
                   std::string direction = "Unknown")
    {
        this->rect = rect;
        this->direction = std::move(direction);
    }
};

class History
{

private:

public:

    int length;
    boost::circular_buffer<std::tuple<int, int, std::string>> history; // Similar to Python deque

    // Standard un-parametrized C-tor
    History()
    {
        this->length = 0;
    };

    explicit History(const int& length)
    {
        this->length = length;
        this->history.resize(this->length);
    }

    void add(const std::tuple<int,int,std::string>& state)
    {
        this->history.push_back(state);
    }

    std::tuple<int, int, std::string> get(const int& index)
    {
        assert(index <= this->history.size());
        assert(index >= 0);
        return this->history[index];
    }

    void set_length(const int& new_length)
    {
        assert(new_length >= this->length);
        this->history.set_capacity(new_length);
        this->length = new_length;
        assert(this->history.capacity() == this->length);
    }

    void view_history()
    {
        for(int h = 0; h < this->history.size(); h++)
        {
            std::cout << " - History index " << h << " : "
                      <<  "(" << std::get<0>(this->history[h]) << ","
                      << std::get<1>(this->history[h]) << ")" << std::endl;
        }
    }
};

class Apple
{
private:

    FakeRect rect;
    int block_size, screen_size;
    unsigned int seed;

public:

    Block apple_block;

    Apple()
    {
        this->block_size = 0;
        this->screen_size = 0;
        this->seed = 0;
        this->rect = FakeRect(0,0,
                                    0,0,
                                    0,0,0,0);
    }

    Apple(const FakeRect& rect,
          const int& screen_size,
          const unsigned int& seed)
    {
        this->rect = rect;
        this->block_size = this->rect.get_size()[0];
        this->screen_size = screen_size;
        this->seed = seed;
    }

    void add_apple_block(const std::vector<std::tuple<int,int>>& available_points)
    {
        int random_index =  random_int(0,(int)available_points.size());
        std::tuple<int,int> random_point = available_points[random_index];
        FakeRect apple_rect = this->rect.clone();
        apple_rect.set_top(std::get<0>(random_point));
        apple_rect.set_left(std::get<1>(random_point));
        this->apple_block = Block(apple_rect);
    }

    void initialize(const std::vector<std::tuple<int,int>>& available_points)
    {
        add_apple_block(available_points);
    }

    FakeRect get_apple()
    {
        return this->apple_block.rect;
    }

};

class Snake
{
private:
    FakeRect rect;
    int block_size, screen_size;
    std::array<std::string, 4> action_space = {"up"  , "down",
                                               "left", "right"};
    std::string unknown_token = "Unknown";

    std::vector<Block> snake_blocks;

    unsigned int seed;

    void update_snake_length()
    {
        this->snake_length = (int)this->snake_blocks.size();
        this->history.set_length(this->snake_length);
    }


    bool colliding_with_wall()
    {
        if((this->snake_blocks[0].rect.get_top() < 0) ||
           (this->snake_blocks[0].rect.get_bottom() > this->screen_size))
        {
            this->dead = true;
            return true;
        }
        if((this->snake_blocks[0].rect.get_left() < 0) ||
           (this->snake_blocks[0].rect.get_right() > this->screen_size))
        {
            this->dead = true;
            return true;
        }
        return false;
    }

    bool colliding_with_self()
    {
        for(int block = 1; block < this->snake_length; block++)
        {
            if (this->snake_blocks[0].rect.get_left() == this->snake_blocks[block].rect.get_left())
            {
                if(this->snake_blocks[0].rect.get_bottom() == this->snake_blocks[block].rect.get_bottom())
                {
                    this->dead = true;
                    return true;
                }
            }
        }
        return false;
    }

public:
    int snake_length = 0;
    History history = History(snake_length);
    bool dead = false;

    // Standard un-parametrized C-tor
    Snake()
    {
        this->block_size = 0;
        this->screen_size = 0;
        this->seed = 0;
    };

    Snake(const FakeRect& rect,
          const int& screen_size,
          const unsigned int& seed)
    {
        this->rect = rect;
        this->screen_size = screen_size;
        this->seed = seed;
        this->block_size = this->rect.get_size()[0];
        this->history.set_length(0);
    }

    void set_direction(std::string direction)
    {
        this->snake_blocks[0].direction = std::move(direction);
    }

    void save_history()
    {

        this->history.add(std::make_tuple(this->snake_blocks[0].rect.get_left(),
                                     this->snake_blocks[0].rect.get_bottom(),
                                     this->snake_blocks[0].direction));
    }

    void move(const int& velocity)
    {
        // Moving head
        std::string dir = this->snake_blocks[0].direction;
        if(dir == "up"){this->snake_blocks[0].rect.move(0, -velocity);}
        if(dir == "down"){this->snake_blocks[0].rect.move(0, velocity);}
        if(dir == "left"){this->snake_blocks[0].rect.move(-velocity, 0);}
        if(dir == "right"){this->snake_blocks[0].rect.move(velocity, 0);}

        // Moving body
        std::tuple<int,int,std::string> hist;
        for(int block = 1; block < this->snake_length; block++)
        {
            hist = this->history.get(block);
            this->snake_blocks[block].rect.set_left(std::get<0>(hist));
            this->snake_blocks[block].rect.set_bottom(std::get<1>(hist));
            this->snake_blocks[block].direction = std::get<2>(hist);
        }
    }

    void add_body_block()
    {
        FakeRect body_rect = this->rect.clone();

        std::tuple<int,int,std::string> hist = this->history.get(0);
        std::string dir = std::get<2>(hist);
        body_rect.set_left(std::get<0>(hist));
        body_rect.set_bottom(std::get<1>(hist));


        Block body_block = Block(body_rect,dir);
        this->snake_blocks.push_back(body_block);
        update_snake_length();
    }

    std::string get_direction(){return this->snake_blocks[0].direction;}

    FakeRect get_head(){return this->snake_blocks[0].rect;}

    FakeRect get_body(const int& index){return this->snake_blocks[index].rect;}

    void initialize(const std::string& direction = "Unknown")
    {
        if(direction == this->unknown_token)
        {
            int random_index = random_int(0,(int)this->action_space.size()-1);
            std::string random_direction = this->action_space[random_index];
            add_head_block(random_direction);
        }
        else
        {
            add_head_block(direction);
        }
    }

    void update(const int& velocity)
    {
        save_history();
        move(velocity);
        if(colliding_with_self() or colliding_with_wall())
        {
            this->dead = true;
            return;
        }
    }

    std::vector<std::tuple<int,int>> available_grid_points()
    {
        int grid_size = this->screen_size / this->block_size;
        std::vector<std::tuple<int,int>> available_grid_points; // Formatted as (top, left)

        for(int y = 0; y < grid_size; y++)
            for(int x = 0; x < grid_size; x++)
            {
                bool is_available = true;
                for(const Block& snake_block: this->snake_blocks)
                {
                    if((snake_block.rect.get_left() == x * this->block_size) &&
                       (snake_block.rect.get_top()  == y * this->block_size))
                    {
                        is_available = false;
                    }
                }
                if(is_available)
                {
                    available_grid_points.emplace_back(std::tuple<int,int>(y * this->block_size,
                                                                  x * this->block_size));
                }
            }
        return available_grid_points;
    }

    bool found_apple(Apple& apple)
    {
        if(get_head().get_left() == apple.apple_block.rect.get_left())
        {
            if(get_head().get_bottom() == apple.apple_block.rect.get_bottom())
            {
                add_body_block();
                apple.initialize(available_grid_points());
                return true;
            }
        }
        return false;
    }


    Eigen::MatrixXi get_grid()
    {
        int grid_size = this->screen_size / this->block_size;
        Eigen::MatrixXi state(grid_size,grid_size);
        state.setZero();
        int head_x, head_y, body_x, body_y;

        head_x = std::floor(this->snake_blocks[0].rect.get_left() / this->block_size);
        head_y = std::floor(this->snake_blocks[0].rect.get_top() / this->block_size);
        state(head_y, head_x) = 2;
        for(int block = 1; block < this->snake_length; block++)
        {
            body_x = std::floor(this->snake_blocks[block].rect.get_left() / this->block_size);
            body_y = std::floor(this->snake_blocks[block].rect.get_top() / this->block_size);
            state(body_y,body_x) = 1;
        }
        return state;
    }

    void view_state()
    {
        std::cout << "  state: \n" << get_grid() << std::endl;
    }

    void add_head_block(const std::string& direction = "Unknown")
    {
        FakeRect head_rect = this->rect.clone();
        int grid_size = std::floor(this->screen_size / this->block_size);
        head_rect.set_left(random_int(0,grid_size) * this->block_size);
        head_rect.set_top(random_int(0,grid_size) * this->block_size);
        if(direction == this->unknown_token)
        {
            int random_index = random_int(0,(int)this->action_space.size()-1);
            std::string random_direction = this->action_space[random_index];
            this->snake_blocks.emplace_back(Block(head_rect,random_direction));
        }
        else
        {
            this->snake_blocks.emplace_back(Block(head_rect,direction));
        }
        update_snake_length();
    }
};


struct RewardConstants {
    int apple_reward;
    int death_reward;
};

struct Dimensions {
    // Assuming square dimensions
    int block_size;
    int screen_size;
};

struct GameSettings {
    int snake_speed;
    int max_steps;
    int seed;
};

class SnakeEnvironment {
private:

public:
    Snake snake = Snake();
    Apple apple = Apple();

    int current_reward = 0;
    int current_score = 0;
    int break_out_counter = 0;

    int running_token = 0; // 0 for false and 1 for true

    RewardConstants reward_constants = {.apple_reward =  1,
            .death_reward = -1};

    Dimensions dimensions = {.block_size  = 30,
            .screen_size = 150};

    GameSettings game_settings = {.snake_speed = dimensions.block_size,
            .max_steps   = 1000,
            .seed = 0};

    bool running = false;

    // C-tor
    SnakeEnvironment( int seed) {
        this->game_settings.seed = seed;
        srand(this->game_settings.seed);
    }

    // Public Methods
    void initialize_environment() {
        FakeRect snake_block_rect = FakeRect(this->dimensions.block_size,
                                                         this->dimensions.block_size);
        this->snake = Snake(snake_block_rect,
                                         this->dimensions.screen_size,
                                         this->game_settings.seed);
        this->snake.initialize();

        FakeRect apple_block_rect = FakeRect(this->dimensions.block_size,
                                                         this->dimensions.block_size);
        this->apple = Apple(apple_block_rect,
                                         this->dimensions.screen_size,
                                         this->game_settings.seed);
        this->apple.initialize(this->snake.available_grid_points());

        this->running = true;
        this->running_token = 1;
    }

    void set_snake_direction(const int &direction_int) {
        if ((direction_int == 0) && (this->snake.get_direction() != "left")) {
            this->snake.set_direction("right");
            return;
        }
        if ((direction_int == 1) && (this->snake.get_direction() != "right")) {
            this->snake.set_direction("left");
            return;
        }
        if ((direction_int == 2) && (this->snake.get_direction() != "down")) {
            this->snake.set_direction("up");
            return;
        }
        if ((direction_int == 3) && (this->snake.get_direction() != "up")) {
            this->snake.set_direction("down");
        }
    }

    std::string get_snake_direction()
    {
        return this->snake.get_direction();
    }

    void step(const int &action) {
        this->current_reward = 0;
        set_snake_direction(action);
        this->snake.update(this->game_settings.snake_speed);
        if (!this->snake.dead) {
            if (this->snake.found_apple(this->apple)) {
                this->current_score += 1;
                this->current_reward += this->reward_constants.apple_reward;
                this->break_out_counter = 0;
            }
        } else {
            this->current_reward += this->reward_constants.death_reward;
            this->running = false;
        }
        if (this->break_out_counter == this->game_settings.max_steps) {
            this->running = false;
        } else {
            this->break_out_counter += 1;
        }
    }

    void view() {
        Eigen::MatrixXi state = this->snake.get_grid();
        int row = (this->apple.get_apple().get_top() / this->dimensions.block_size);
        int col = (this->apple.get_apple().get_left() / this->dimensions.block_size);
        state(row, col) = 5;
        std::cout << "state: \n" << state << std::endl;
    }

    bool get_status() {
        return this->running;
    }

    float get_reward() {
        return this->current_reward;
    }

    std::vector<int> get_state() {
        FakeRect head = this->snake.get_head();
        std::vector<int> _wall_danger_state{0, 0, 0, 0};
        if (head.get_top() == 0) { _wall_danger_state[0] = 1; }
        if (head.get_bottom() == this->dimensions.screen_size) { _wall_danger_state[1] = 1; }
        if (head.get_left() == 0) { _wall_danger_state[2] = 1; }
        if (head.get_right() == this->dimensions.screen_size) { _wall_danger_state[3] = 1; }

        std::vector<int> _snake_danger_state{0, 0, 0, 0};
        for (int body = 1; body < this->snake.snake_length; body++) {
            if (head.get_left() == this->snake.get_body(body).get_left()) {
                if (head.get_top() == this->snake.get_body(body).get_bottom()) {
                    _snake_danger_state[0] = 1;
                } else if (head.get_bottom() == this->snake.get_body(body).get_top()) {
                    _snake_danger_state[1] = 1;
                }
            }
            if (head.get_top() == this->snake.get_body(body).get_top()) {
                if (head.get_left() == this->snake.get_body(body).get_right()) {
                    _snake_danger_state[2] = 1;
                } else if (head.get_right() == this->snake.get_body(body).get_left()) {
                    _snake_danger_state[3] = 1;
                }
            }
        }
        _wall_danger_state.insert(_wall_danger_state.end(), _snake_danger_state.begin(), _snake_danger_state.end());

        std::vector<int> _apple_state{0, 0, 0, 0};
        FakeRect apple = this->apple.get_apple();
        if (apple.get_bottom() <= head.get_top()) { _apple_state[0] = 1; }
        if (apple.get_top() >= head.get_bottom()) { _apple_state[1] = 1; }
        if (apple.get_right() <= head.get_left()) { _apple_state[2] = 1; }
        if (apple.get_left() >= head.get_right()) { _apple_state[3] = 1; }


        std::vector<int> _direction_state{0, 0, 0, 0};
        if( this->snake.get_direction() == "right"){_direction_state[0] = 1;}
        if( this->snake.get_direction() == "left"){_direction_state[1] = 1;}
        if( this->snake.get_direction() == "up"){_direction_state[2] = 1;}
        if( this->snake.get_direction() == "down"){_direction_state[3] = 1;}

        _apple_state.insert(_apple_state.end(), _direction_state.begin(), _direction_state.end());

        _wall_danger_state.insert(_wall_danger_state.end(), _apple_state.begin(), _apple_state.end());

        return _wall_danger_state;
    }



};

namespace py = pybind11;

PYBIND11_MODULE(SnakeLogic, handle)
{
    handle.doc() = "The Snake game logic class. ";
    py::class_<SnakeEnvironment>(handle, "SnakeEnvironment")
            .def(py::init<int>())
            .def("get_state", &SnakeEnvironment::get_state)
            .def("get_reward", &SnakeEnvironment::get_reward)
            .def("get_status", &SnakeEnvironment::get_status)
            .def("view", &SnakeEnvironment::view)
            .def("step", &SnakeEnvironment::step)
            .def("initialize_environment", &SnakeEnvironment::initialize_environment)
            .def("set_snake_direction", &SnakeEnvironment::set_snake_direction)
            .def("get_snake_direction", &SnakeEnvironment::get_snake_direction);
}


