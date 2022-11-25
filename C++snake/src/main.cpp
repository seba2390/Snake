// STL includes
#include <iostream>
#include <list> // for std::list
#include <array> // for std::array
#include <cstdlib> // for rng

// Boost and Eigen include
#include <boost/circular_buffer.hpp>
#include <Eigen/Dense>
#include <Eigen/Sparse>

// TODO: Implement setting seed for srand()
// TODO: Fix recursiveness for setters in FakeRect
// TODO: Investigate endless loop in move() in snake class

namespace Util
{
    int random_int(const int& low,
                   const int& high)
    {
        return rand() % (high-1) + low;
    }

    class FakeRect
    {
    private:
        int height;
        int width;
        std::array<int,2> size = {};
    public:
        int _centerx, _centery, _left, _right, _top, _bottom;

        // Standard C-tor
        FakeRect(){};

        // Parametrized C-tor
        [[maybe_unused]] FakeRect(
                      const int& height,
                      const int& width,
                      int centerx = 0,
                      int centery = 0,
                      int left = 0,
                      int right = 0,
                      int top = 0,
                      int bottom = 0)
        {
            // Private const definitions.
            this->height = (height);
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
        int get_centerx(){return this->_centerx;}
        void set_centerx(int centerx)
        {
            this->_centerx = centerx;
            set_left(this->_centerx-(int)(this->width/2));
            set_right(this->_centerx+(int)(this->width/2));
        }

        int get_centery(){return this->_centery;}
        void set_centery(int centery)
        {
            this->_centery = centery;
            set_top(this->_centery-(int)(this->height/2));
            set_bottom(this->_centery+(int)(this->height/2));
        }

        int get_left(){return this->_left;}
        void set_left(int left)
        {
            this->_left = left;
            set_right(this->_left+this->width);
            set_centerx(this->_left+(int)(this->width/2));
        }

        int get_right(){return this->_right;}
        void set_right(int right)
        {
            this->_right = right;
            set_left(this->_right-this->width);
            set_centerx(this->_right-(int)(this->width/2));
        }

        int get_top() const{return this->_top;}
        void set_top(int top)
        {
            this->_top = top;
            set_bottom(this->_top+this->height);
            set_centery(this->_top+(int)(this->height/2));
        }

        int get_bottom(){return this->_bottom;}
        void set_bottom(int bottom)
        {
            this->_bottom = bottom;
            set_top(this->_bottom-this->height);
            set_centery(this->_bottom-(int)(this->height/2));
        }

        std::array<int,2> get_size(){return this->size;}
    };

}

namespace GameObjects
{
    class Block
    {
    public:

        Util::FakeRect rect;
        std::string direction;

        // Standard un-parametrized C-tor
        Block()= default;

        explicit Block(const Util::FakeRect& rect,
                       std::string direction = "Unknown")
       {
            this->rect = rect;
            this->direction = direction;
       }
    };

    class History
    {

    private:
        int content_counter = 0;

    public:

        int length = 0;
        boost::circular_buffer<std::tuple<int, int, std::string>> history; // Similar to Python deque

        // Standard un-parametrized C-tor
        History()= default;

        explicit History(const int& length)
        {
            this->length = length;
            this->history.set_capacity(this->length);
        }

        void add(const std::tuple<int,int,std::string>& state)
        {
            this->history.push_back(state);
        }

        std::tuple<int, int, std::string> get(const int& index){return this->history[index];}

        void set_length(const int& new_length){this->history.set_capacity(new_length);}
    };

    class Apple
    {
    private:

        Util::FakeRect rect;
        int block_size, screen_size;
        unsigned int seed;

    public:

        Block apple_block;

        Apple(const Util::FakeRect& rect,
              const int& screen_size,
              const unsigned int& seed)
        {
            this->rect = rect;
            this->block_size = this->rect.get_size()[0];
            this->screen_size = screen_size;
            this->seed = seed;
        }

        void add_apple_block();
    };

    class Snake
    {
    private:
        Util::FakeRect rect;
        int block_size, screen_size;
        std::array<std::string, 4> action_space = {"up"  , "down",
                                                   "left", "right"};
        std::string unknown_token = "Unknown";

        std::vector<Block> snake_blocks;
        int snake_length = 0;
        History history = History(snake_length);
        unsigned int seed;

        void update_snake_length()
        {
            this->snake_length = (int)this->snake_blocks.size();
            this->history.set_length(this->snake_length);
        }

        void add_head_block(const std::string& direction = "Unknown")
        {
            Util::FakeRect head_rect = this->rect.clone();
            int grid_size = this->screen_size / this->block_size;
            head_rect.set_left(Util::random_int(0,grid_size));
            head_rect.set_top(Util::random_int(0,grid_size));
            if(direction == this->unknown_token)
            {
                int random_int = Util::random_int(0,(int)this->action_space.size()-1);
                std::string random_direction = this->action_space[random_int];
                this->snake_blocks.push_back(Block(head_rect,random_direction));
            }
            else
            {
                this->snake_blocks.push_back(Block(head_rect,direction));
            }
            update_snake_length();
        }

        void add_body_block()
        {
            Util::FakeRect body_rect = this->rect.clone();
            std::map<std::string, std::tuple<int,int>> map{{"up"   , std::tuple(0, this->block_size)},
                                                           {"down" , std::tuple(0,-this->block_size)},
                                                           {"left" , std::tuple( this->block_size,0)},
                                                           {"right", std::tuple(-this->block_size,0)}};
            std::tuple<int,int,std::string> hist = this->history.get(0);
            std::string dir = std::get<2>(hist);
            body_rect.set_left(std::get<0>(hist)+std::get<0>(map[dir]));
            body_rect.set_bottom(std::get<1>(hist)+std::get<1>(map[dir]));
            Block body_block = Block(body_rect,dir);
            this->snake_blocks.push_back(body_block);
            update_snake_length();
        }

        void move(const int& velocity)
        {
            // Moving head
            std::map<std::string, std::tuple<int,int>> map{{"up"  , std::tuple(0,-velocity)},
                                                           {"down" , std::tuple(0,velocity)},
                                                           {"left", std::tuple(-velocity,0)},
                                                           {"right", std::tuple(velocity,0)}};
            std::string dir = this->snake_blocks[0].direction;
            int head_vx = std::get<0>(map[dir]);
            int head_vy = std::get<1>(map[dir]);
            this->snake_blocks[0].rect.move(head_vx, head_vy);

            // Moving body
            if(this->snake_length > 1)
            {
                std::tuple<int,int,std::string> hist;
                for(int block = 1; block < this->snake_length; block++)
                {
                    hist = this->history.get(-(this->snake_length-block));
                    this->snake_blocks[block].rect.set_left(std::get<0>(hist));
                    this->snake_blocks[block].rect.set_bottom(std::get<1>(hist));
                    this->snake_blocks[block].direction = std::get<2>(hist);
                }
            }
        }
        void set_direction(std::string direction)
        {
            this->snake_blocks[0].direction = std::move(direction);
        }

        std::string get_direction(){return this->snake_blocks[0].direction;}

        Util::FakeRect get_head(){return this->snake_blocks[0].rect;}

        Util::FakeRect get_body(const int& index){return this->snake_blocks[index].rect;}

        void initialize(const std::string& direction = "Unknown")
        {
            if(direction == this->unknown_token)
            {
                int random_int = Util::random_int(0,(int)this->action_space.size()-1);
                std::string random_direction = this->action_space[random_int];
                add_head_block(random_direction);
            }
            else
            {
                add_head_block(direction);
            }
            save_history();
        }

        void save_history()
        {
            this->history.add(std::tuple(this->snake_blocks[0].rect.get_left(),
                                               this->snake_blocks[0].rect.get_bottom(),
                                               this->snake_blocks[0].direction));
        }

        bool colliding_with_wall()
        {
            if((this->snake_blocks[0].rect.get_top() < 0) ||
               (this->snake_blocks[0].rect.get_bottom() > this->screen_size))
            {
                return true;
            }
            if((this->snake_blocks[0].rect.get_left() < 0) ||
                (this->snake_blocks[0].rect.get_right() > this->screen_size))
            {
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
                        return true;
                    }
                }
            }
            return false;
        }



    public:
        bool dead = false;

        // Standard un-parametrized C-tor
        Snake() = default;

        Snake(const Util::FakeRect& rect,
              const int& screen_size,
              const unsigned int& seed)
        {
            this->rect = rect;
            this->screen_size = screen_size;
            this->seed = seed;
        }


    };
}

int main()
{
    using std::cout; using std::endl;

    cout << Util::random_int(0,10) << endl;
    cout << Util::random_int(0,10) << endl;

    std::array<std::string,2> test = {"a", "b"};
    cout << test.size() << endl;
    cout << test[test.size()-1] << endl;

    std::map<std::string, std::tuple<int,int>> map{{"up", std::tuple(0,1)}, {"down", std::tuple(2,3)},
                                                   {"left", std::tuple(4,5)}, {"right", std::tuple(6,7)}};
    cout << std::get<1>(map["up"]) << endl;



}