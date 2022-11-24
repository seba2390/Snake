// C++ includes
#include <iostream>
#include <list> // for std::list

// Boost include
#include <boost/circular_buffer.hpp>

namespace Util
{
    class FakeRect
    {
    private:
        int height;
        int width;
        int size[2] = {};
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

        int get_top(){return this->_top;}
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

        int* get_size(){return this->size;}
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
        Block() = default;

        Block(const Util::FakeRect& rect,
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

        int length;
        boost::circular_buffer<std::tuple<int, int>> history; // Similar to Python deque

        History(const int& length)
        {
            this->length = length;
            this->history.set_capacity(this->length);
        }

        void add(const std::tuple<int,int>& state)
        {
            this->history.push_back(state);
        }

        std::tuple<int, int> get(const int& index){return this->history[index];}

        void set_length(const int& new_length){this->history.set_capacity(new_length);}
    };

    class Apple
    {
    private:

        Util::FakeRect rect;
        int block_size, screen_size;

    public:

        Block apple_block;

        Apple(const Util::FakeRect& rect,
              const int& screen_size,
              const int& seed)
        {
            this->rect = rect;
            this->block_size = this->rect.get_size()[0];
            this->screen_size = screen_size;
        }

        void add_apple_block();
    };
}

int main()
{

}